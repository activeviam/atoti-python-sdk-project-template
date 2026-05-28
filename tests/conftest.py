from collections.abc import AsyncGenerator
from pathlib import Path

import atoti as tt
import pytest

from app import Config, start_app

_TESTS_DIRECTORY = Path(__file__).parent
_PROJECT_DIRECTORY = _TESTS_DIRECTORY.parent


@pytest.fixture(name="project_name", scope="session")
def project_name_fixture() -> str:
    return _PROJECT_DIRECTORY.name


@pytest.fixture(name="config", scope="session")
def config_fixture() -> Config:
    return Config(
        port=0,
    )


@pytest.fixture(
    name="session",
    # Don't use this fixture in tests mutating the app or its underlying session.
    scope="session",
)
async def session_fixture(config: Config) -> AsyncGenerator[tt.Session]:
    async with start_app(config=config) as session:
        with tt.mapping_lookup(check=False):
            yield session
