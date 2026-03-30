from collections.abc import Mapping, Set as AbstractSet
from typing import Annotated, TypedDict

from .node import Node

type _ColumnSkeleton = Annotated[str, Node(key_length=2)]
type _TableSkeleton = Annotated[AbstractSet[_ColumnSkeleton], Node()]
type _TablesSkeleton = Mapping[str, _TableSkeleton]

type _LevelSkeleton = Annotated[str, Node(key_length=3)]
type _HierarchySkeleton = Annotated[AbstractSet[_LevelSkeleton], Node(key_length=2)]
type _DimensionSkeleton = Mapping[str, _HierarchySkeleton]
type _DimensionsSkeleton = Mapping[str, _DimensionSkeleton]

type _MeasureSkeleton = Annotated[str, Node()]
type _MeasuresSkeleton = AbstractSet[_MeasureSkeleton]


class __CubeSkeleton(TypedDict):
    dimensions: _DimensionsSkeleton
    measures: _MeasuresSkeleton


type _CubeSkeleton = Annotated[__CubeSkeleton, Node()]

type _CubesSkeleton = Mapping[str, _CubeSkeleton]


class Skeleton(TypedDict):
    tables: _TablesSkeleton
    cubes: _CubesSkeleton
