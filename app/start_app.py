from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, nullcontext

import atoti as tt
import httpx
from opentelemetry.instrumentation.httpx import AsyncOpenTelemetryTransport

from .config import Config
from .load_tables import load_tables
from .start_session import start_session
from .util import run_periodically


@asynccontextmanager
async def start_app(*, config: Config) -> AsyncGenerator[tt.Session]:
    httpx_transport = AsyncOpenTelemetryTransport(httpx.AsyncHTTPTransport())
    async with (
        httpx.AsyncClient(transport=httpx_transport) as http_client,
        start_session(config=config, http_client=http_client) as session,
        run_periodically(
            lambda: load_tables(session, config=config, http_client=http_client),
            period=config.data_refresh_period,
        )
        if config.data_refresh_period
        else nullcontext(),
    ):
        yield session
