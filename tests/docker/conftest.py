from collections.abc import Generator
from contextlib import closing
from datetime import timedelta
from subprocess import STDOUT, CalledProcessError, check_output
from time import monotonic, sleep

import atoti as tt
import docker
import pytest


@pytest.fixture(name="docker_client", scope="session")
def docker_client_fixture() -> Generator[docker.DockerClient]:
    with closing(docker.from_env()) as client:
        yield client


@pytest.fixture(name="docker_image_id", scope="session")
def docker_image_id_fixture(docker_client: docker.DockerClient) -> Generator[str]:
    # The `Dockerfile` uses `RUN --mount` which requires BuildKit.
    # BuildKit is not supported by Docker's Python SDK so `docker_client.images.build` cannot be used.
    # See https://github.com/docker/docker-py/issues/2230.
    try:
        # `--quiet` makes the built image ID the only output, removing the need to tag the image.
        image_id = check_output(
            [  # noqa: S607
                "docker",
                "build",
                "--quiet",
                ".",
            ],
            stderr=STDOUT,
            text=True,
        ).strip()
    except CalledProcessError as error:
        raise RuntimeError(f"Docker build failed:\n{error.output}") from error

    try:
        yield image_id
    finally:
        docker_client.images.remove(image_id)


@pytest.fixture(name="session_inside_docker_container", scope="session")
def session_inside_docker_container_fixture(
    docker_client: docker.DockerClient, docker_image_id: str
) -> Generator[tt.Session]:
    container = docker_client.containers.run(
        docker_image_id,
        detach=True,
        environment={
            # Test external APIs.
            "DATA_REFRESH_PERIOD": "30"
        },
        publish_all_ports=True,
    )

    try:
        deadline = monotonic() + timedelta(minutes=1).total_seconds()
        while b"Session listening on port" not in (logs := container.logs()):
            if monotonic() > deadline:
                raise RuntimeError(f"Session start timed out:\n{logs.decode()}")
            sleep(0.1)

        container.reload()  # Refresh `attrs` to get its `HostPort`.
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
    finally:
        container.stop()
        container.remove()
