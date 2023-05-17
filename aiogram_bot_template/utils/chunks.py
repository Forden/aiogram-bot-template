import collections.abc
import typing

T = typing.TypeVar("T")


def chunks(
    list_to_split: typing.Sequence[T], chunk_size: int
) -> collections.abc.Iterator[typing.Sequence[T]]:
    for i in range(0, len(list_to_split), chunk_size):
        yield list_to_split[i : i + chunk_size]
