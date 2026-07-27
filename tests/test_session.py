import atoti as tt
import pandas as pd

from app import Skeleton

from .expected_total_capacity import EXPECTED_TOTAL_CAPACITY


async def test_total_capacity(session: tt.Session) -> None:
    skeleton = Skeleton.cubes.STATION
    cube = session.cubes[skeleton.name]
    m = cube.measures
    result = cube.query(m[skeleton.measures.CAPACITY.name])
    expected_result = pd.DataFrame(
        {
            skeleton.measures.CAPACITY.name: pd.Series(
                [EXPECTED_TOTAL_CAPACITY], dtype="Int32"
            ),
        }
    )
    pd.testing.assert_frame_equal(result, expected_result)


async def test_departments(session: tt.Session) -> None:
    skeleton = Skeleton.cubes.STATION
    cube = session.cubes[skeleton.name]
    l, m = cube.levels, cube.measures
    result = cube.query(
        m[skeleton.measures.CONTRIBUTORS_COUNT.name],
        levels=[
            l[skeleton.dimensions.STATION_INFORMATION.LOCATION.DEPARTMENT.key],
        ],
    )
    assert list(result.index) == [
        "75, Paris, Île-de-France",
        "92, Hauts-de-Seine, Île-de-France",
        "93, Seine-Saint-Denis, Île-de-France",
        "94, Val-de-Marne, Île-de-France",
        "95, Val-d'Oise, Île-de-France",
    ]
