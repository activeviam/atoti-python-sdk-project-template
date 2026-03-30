from asyncio import to_thread
from collections.abc import Awaitable, Callable, Iterable, Mapping, Set as AbstractSet
from functools import wraps
from io import BytesIO, StringIO
from pathlib import Path
from typing import IO, Concatenate

import httpx
import pandas as pd
from pydantic import HttpUrl

_Coordinates = tuple[float, float]  # (latitude, longitude)

_ReverseGeocodedCoordinates = dict[_Coordinates, dict[str, str]]

_COORDINATES_COLUMN_NAMES: Iterable[str] = ["latitude", "longitude"]

_COLUMN_NAME_MAPPING: Mapping[str, str] = {
    "result_context": "department",
    "result_city": "city",
    "result_postcode": "postcode",
    "result_street": "street",
    "result_housenumber": "house_number",
}


def _cache[**P](
    function: Callable[
        Concatenate[AbstractSet[_Coordinates], P],
        Awaitable[_ReverseGeocodedCoordinates],
    ],
    /,
) -> Callable[
    Concatenate[AbstractSet[_Coordinates], P], Awaitable[_ReverseGeocodedCoordinates]
]:
    cache: _ReverseGeocodedCoordinates = {}

    @wraps(function)
    async def function_wrapper(
        coordinates: AbstractSet[_Coordinates],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> _ReverseGeocodedCoordinates:
        uncached_coordinates = coordinates - set(cache)
        result = await function(uncached_coordinates, *args, **kwargs)
        cache.update(result)
        return {key: value for key, value in cache.items() if key in coordinates}

    return function_wrapper


def _to_csv(df: pd.DataFrame, /) -> IO[bytes]:
    file = BytesIO()
    df.to_csv(file, index=False)
    file.seek(0)
    return file


@_cache
async def _reverse_geocode(
    coordinates: AbstractSet[_Coordinates],
    /,
    *,
    http_client: httpx.AsyncClient,
    reverse_geocoding_path: HttpUrl | Path,
) -> _ReverseGeocodedCoordinates:
    if not coordinates:
        return {}

    data: StringIO | Path
    coordinates_df = pd.DataFrame(coordinates, columns=list(_COORDINATES_COLUMN_NAMES))

    if isinstance(reverse_geocoding_path, Path):
        data = reverse_geocoding_path
    else:
        file = await to_thread(_to_csv, coordinates_df)
        response = await http_client.post(
            str(reverse_geocoding_path),
            data={"result_columns": list(_COLUMN_NAME_MAPPING)},
            files={"data": file},
        )
        response.raise_for_status()
        data = StringIO(response.text)

    result_df = pd.read_csv(data)
    assert len(result_df) == len(coordinates_df)

    # The returned coordinates are not strictly equal to the input ones.
    # They may have slightly moved.
    # Using input ones to allow the caller to look up the addresses of the coordinates it has.
    for column_name in coordinates_df.columns:
        result_df[column_name] = coordinates_df[column_name]

    result_df = result_df.set_index(list(coordinates_df.columns))
    result_df = result_df.rename(columns=_COLUMN_NAME_MAPPING)
    return result_df.to_dict("index")  # ty: ignore[invalid-return-type]


async def reverse_geocode(
    coordinates: Iterable[_Coordinates],
    /,
    *,
    http_client: httpx.AsyncClient,
    reverse_geocoding_path: HttpUrl | Path,
) -> pd.DataFrame:
    data = await _reverse_geocode(
        set(coordinates),
        http_client=http_client,
        reverse_geocoding_path=reverse_geocoding_path,
    )
    result_df = pd.DataFrame.from_dict(data, orient="index")
    index = result_df.index.set_names(_COORDINATES_COLUMN_NAMES)
    result_df.index = index
    return result_df.reset_index()
