from collections.abc import Generator, Mapping
from contextlib import contextmanager
from uuid import uuid4

import docker
from docker.models.containers import Container


@contextmanager
def docker_container(
    image_name: str,
    /,
    *,
    client: docker.DockerClient,
    container_name: str | None = None,
    env: Mapping[str, str] | None = None,
) -> Generator[Container]:
    container = client.containers.run(
        image_name,
        detach=True,
        environment=env,
        name=container_name or str(uuid4()),
        publish_all_ports=True,
    )
    yield container
    container.stop()
    container.remove()
