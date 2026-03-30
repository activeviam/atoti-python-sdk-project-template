import atoti as tt

from .opentelemetry import traced
from .skeleton import Skeleton
from .util import column, fact_based_hierarchy


@traced
def create_station_cube(session: tt.Session, /) -> None:
    skeleton = Skeleton.cubes.STATION

    cube = session.create_cube(
        session.tables[Skeleton.tables.STATION_STATUS.name],
        skeleton.name,
        mode="manual",
    )
    h, l, m = cube.hierarchies, cube.levels, cube.measures

    h.update(
        [
            fact_based_hierarchy(
                session,
                skeleton.dimensions.STATION_INFORMATION.LOCATION,
                lambda hierarchy: {
                    hierarchy.DEPARTMENT: Skeleton.tables.STATION_INFORMATION.DEPARTMENT,
                    hierarchy.CITY: Skeleton.tables.STATION_INFORMATION.CITY,
                    hierarchy.POSTCODE: Skeleton.tables.STATION_INFORMATION.POSTCODE,
                    hierarchy.STREET: Skeleton.tables.STATION_INFORMATION.STREET,
                    hierarchy.HOUSE_NUMBER: Skeleton.tables.STATION_INFORMATION.HOUSE_NUMBER,
                },
            ),
            fact_based_hierarchy(
                session,
                skeleton.dimensions.STATION_INFORMATION.STATION,
                lambda hierarchy: {
                    hierarchy.NAME: Skeleton.tables.STATION_INFORMATION.NAME,
                    hierarchy.ID: Skeleton.tables.STATION_INFORMATION.ID,
                },
            ),
            fact_based_hierarchy(
                session,
                skeleton.dimensions.STATION_STATUS.BIKE_TYPE,
                lambda hierarchy: {
                    hierarchy.BIKE_TYPE: Skeleton.tables.STATION_STATUS.BIKE_TYPE,
                },
            ),
        ]
    )

    with session.data_model_transaction():
        m[skeleton.measures.BIKES.name] = tt.agg.sum(
            column(session, Skeleton.tables.STATION_STATUS.BIKES)
        )
        m[skeleton.measures.CAPACITY.name] = tt.agg.sum(
            tt.agg.single_value(
                column(session, Skeleton.tables.STATION_INFORMATION.CAPACITY)
            ),
            scope=tt.OriginScope(
                {l[skeleton.dimensions.STATION_INFORMATION.STATION.ID.key]}
            ),
        )


@traced
def create_cubes(session: tt.Session, /) -> None:
    create_station_cube(session)
