import re
from collections.abc import Mapping, Set as AbstractSet
from itertools import count
from os import linesep
from textwrap import dedent
from typing import Annotated, TypeAliasType, get_args, get_origin

from pydantic import TypeAdapter
from typing_extensions import is_typeddict

from .node import Node

_COUNTER = count()


def _generate_unique_class_name() -> str:
    return f"_Generated{next(_COUNTER)}"


def _identifier(name: str, /) -> str:
    return re.sub(r"\W|^(?=\d)", "_", name)


def _indent(code: str, /) -> str:
    return f"{' ' * 4}{code}"


_KEY_PROPERTY_NAME = "key"
_NAME_PROPERTY_NAME = "name"


def _unwrap_type[T](type_: type[T], /) -> tuple[type[T], Node | None]:
    if isinstance(type_, TypeAliasType):
        return _unwrap_type(type_.__value__)
    match get_origin(type_), get_args(type_):
        case origin, (unwrapped_type, (Node() as node)) if origin is Annotated:
            return unwrapped_type, node
        case _:
            return type_, None


SKELETON_CLASS_NAME = "Skeleton"

_SKELETON_DOCSTRING = dedent('''\
    """The skeleton of the application.

    It mirrors the structure of the data model but only declares the parent/child relationship between nodes.

    Note:
        Attaching other information to the skeleton is discouraged because this will end up duplicating the data model API already provided by Atoti.
        For instance, it is discouraged to add a ``data_type`` attribute to ``Column``, or a ``keys`` attribute to ``Table``.

    Skeletons scale well to large data models because IDEs can inspect them statically and thus offer:

    * Autocompletion
    * "Find all references"
    * "Go to definition"
    * Type checking
    """
''')


def _generate_class_name_and_lines[T](
    skeleton: T,
    skeleton_type: type[T],
    /,
    *,
    is_root: bool = False,
    path: tuple[str, ...],
) -> tuple[str, list[str]]:
    skeleton_type, node = _unwrap_type(skeleton_type)

    match get_origin(skeleton_type), get_args(skeleton_type):
        case None, ():
            match skeleton_type:
                case _ if skeleton_type is str:
                    class_name_and_lines_from_attribute_name: dict[
                        str, tuple[str, list[str]]
                    ] = {}
                case typed_dict if is_typeddict(typed_dict):
                    assert isinstance(skeleton, Mapping)
                    class_name_and_lines_from_attribute_name = {
                        attribute_name: _generate_class_name_and_lines(
                            skeleton[attribute_name],
                            annotation,
                            path=path,
                        )
                        for attribute_name, annotation in typed_dict.__annotations__.items()
                    }
                case _:
                    raise TypeError(f"Unsupported skeleton type: {skeleton_type}.")
        case origin, (element_type,) if origin is AbstractSet:
            assert isinstance(skeleton, AbstractSet)
            class_name_and_lines_from_attribute_name = {
                _identifier(str(child_name)).upper(): _generate_class_name_and_lines(
                    child_name,
                    element_type,
                    path=(*path, str(child_name)),
                )
                for child_name in skeleton
            }
        case origin, (name_type, value_type) if origin is Mapping:
            assert isinstance(skeleton, Mapping)
            assert name_type is str
            class_name_and_lines_from_attribute_name = {
                _identifier(str(child_name)).upper(): _generate_class_name_and_lines(
                    skeleton[child_name],
                    value_type,
                    path=(*path, str(child_name)),
                )
                for child_name in skeleton
            }
        case _:
            raise TypeError(f"Unsupported skeleton type: {skeleton_type}.")

    return (
        class_name := SKELETON_CLASS_NAME if is_root else _generate_unique_class_name(),
        [
            *(
                line
                for _, _lines in class_name_and_lines_from_attribute_name.values()
                for line in _lines
            ),
            "@final",
            f"class {class_name}:",
            *(
                _indent(line)
                for line in [
                    *(_SKELETON_DOCSTRING.splitlines() if is_root else []),
                    *(
                        []
                        if node is None
                        else [
                            *(
                                []
                                if node.key_length is None
                                else [
                                    f"{_KEY_PROPERTY_NAME}: Final = {path[-node.key_length :]}"
                                ]
                            ),  # Using a tuple instead of a string to let Python handle quoting.
                            f"{_NAME_PROPERTY_NAME}: Final = {(path[-1],)}[0]",
                        ]
                    ),
                    *[
                        f"{attribute_name}: Final = {class_name}"
                        for attribute_name, (
                            class_name,
                            _,
                        ) in class_name_and_lines_from_attribute_name.items()
                    ],
                ]
            ),
        ],
    )


def generate[T](skeleton: T, skeleton_type: type[T], /) -> str:
    skeleton = TypeAdapter(skeleton_type).validate_python(skeleton)
    _, lines = _generate_class_name_and_lines(
        skeleton, skeleton_type, is_root=True, path=()
    )
    lines = [
        "# Generated skeleton, do not edit.",
        "from typing import Final, final",
        *lines,
    ]
    assert not any(linesep in line for line in lines)
    return linesep.join(lines)
