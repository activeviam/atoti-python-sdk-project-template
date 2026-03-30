from asyncio import run, to_thread
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from . import Config, start_app


def _setup_opentelemetry() -> None:
    resource = Resource.create({"service.name": "app"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)


async def main() -> None:
    _setup_opentelemetry()
    async with start_app(config=Config()) as session:
        port = urlparse(session.url).port or 80
        print(f"Session listening on port {port}")  # noqa: T201
        await to_thread(session.wait)


run(main())
