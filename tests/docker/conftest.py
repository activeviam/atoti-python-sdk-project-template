from collections.abc import Generator
from contextlib import closing
from datetime import timedelta
from pathlib import Path
from shutil import which
from uuid import uuid4

import atoti as tt
import docker
import pytest

from ._docker_container import docker_container
from ._run_command import run_command
from ._timeout import Timeout


@pytest.fixture(name="docker_bin", scope="session")
def docker_bin_fixture() -> Path:
    docker_bin = which("docker")
    assert docker_bin
    return Path(docker_bin)


@pytest.fixture(name="docker_client", scope="session")
def docker_client_fixture() -> Generator[docker.DockerClient]:
    with closing(docker.from_env()) as client:
        yield client


@pytest.fixture(name="docker_image_name", scope="session")
def docker_image_name_fixture(
    docker_bin: Path, docker_client: docker.DockerClient, project_name: str
) -> Generator[str]:
    tag = f"{project_name}:{uuid4()}"

    # BuildKit is enabled by default for all users on Docker Desktop.
    # See https://docs.docker.com/build/buildkit/#getting-started.
    is_buildkit_already_enabled = (
        "docker desktop" in run_command([str(docker_bin), "version"]).lower()
    )

    # BuildKit is not supported by Docker's Python SDK so `docker_client.images.build` cannot be used.
    # See https://github.com/docker/docker-py/issues/2230.
    output = run_command(
        [str(docker_bin), "build", "--tag", tag, "."],
        env=None if is_buildkit_already_enabled else {"DOCKER_BUILDKIT": "1"},
    )
    assert f"naming to docker.io/library/{tag}" in output
    yield tag
    docker_client.images.remove(tag)


@pytest.fixture(name="session_inside_docker_container", scope="session")
def session_inside_docker_container_fixture(
    docker_client: docker.DockerClient, docker_image_name: str
) -> Generator[tt.Session]:
    timeout = Timeout(timedelta(minutes=1))

    with docker_container(
        docker_image_name,
        client=docker_client,
        env={
            # Test external APIs.
            "DATA_REFRESH_PERIOD": "30"
        },
    ) as container:
        while True:
            logs = container.logs()
            if b"Session listening on port" in logs:
                break
            if timeout.timed_out:
                raise RuntimeError(f"Session start timed out:\n{logs}")

        container.reload()  # Refresh `attrs` to get its `HostPort`.
        assert container.attrs is not None
        host_port = int(
            next(iter(container.attrs["NetworkSettings"]["Ports"].values()))[0][
                "HostPort"
            ]
        )
        with (
            tt.Session.connect(f"http://localhost:{host_port}") as session,
            tt.mapping_lookup(check=False),
        ):
            yield session
