import sys
from asyncio import to_thread
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import atoti as tt
import httpx

from .config import Config
from .create_and_join_tables import create_and_join_tables
from .create_cubes import create_cubes
from .load_tables import load_tables
from .opentelemetry import span


@span
def _create_data_model(session: tt.Session, /) -> None:
    create_and_join_tables(session)
    create_cubes(session)


@asynccontextmanager
async def start_session(
    *,
    config: Config,
    http_client: httpx.AsyncClient,
) -> AsyncGenerator[tt.Session]:
    """Start the session, declare the data model and load the initial data."""
    session_config = tt.SessionConfig(
        logging=tt.LoggingConfig(destination=sys.stdout),
        port=config.port,
    )
    session = await to_thread(tt.Session.start, session_config)
    try:
        with tt.mapping_lookup(check=config.check_mapping_lookups):
            await to_thread(_create_data_model, session)
        await load_tables(session, config=config, http_client=http_client)
        yield session
    finally:
        await to_thread(session.close)
