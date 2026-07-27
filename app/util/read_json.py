import json
from asyncio import to_thread
from pathlib import Path

import anyio
import httpx2
from pydantic import HttpUrl


async def read_json(
    base_path: HttpUrl | Path,
    file_path: Path,
    /,
    *,
    http_client: httpx2.AsyncClient,
) -> object:
    if isinstance(base_path, Path):
        json_bytes = await anyio.Path(base_path / file_path).read_bytes()
    else:
        url = f"{base_path}/{file_path.as_posix()}"
        response = await http_client.get(url)
        response.raise_for_status()
        json_bytes = await response.aread()
    # Parse JSON in separate thread to not block the event loop.
    return await to_thread(json.loads, json_bytes)
