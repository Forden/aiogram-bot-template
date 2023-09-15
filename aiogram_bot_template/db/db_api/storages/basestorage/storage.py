import typing
from typing import Any, Optional, TypeVar

T = TypeVar("T")


class SingleQueryResult:
    def __init__(self, result: Optional[typing.Mapping[str, Any]]):
        self._data = {**result} if result else None

    @property
    def data(self) -> Optional[dict[str, Any]]:
        return self._data

    def convert(self, model: type[T]) -> Optional[T]:
        return model(**self.data) if self._data else None


class MultipleQueryResults:
    def __init__(self, results: list[typing.Mapping[str, Any]]):
        self._data: list[dict[str, Any]] = [{**i} for i in results]

    @property
    def data(self) -> list[dict[str, Any]]:
        return self._data

    def convert(self, model: type[T]) -> list[T]:
        return [model(**i) for i in self._data]


class RawConnection:
    async def _fetch(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[Any] = None,
    ) -> MultipleQueryResults:
        raise NotImplementedError

    async def _fetchrow(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[Any] = None,
    ) -> SingleQueryResult:
        raise NotImplementedError

    async def _execute(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[Any] = None,
    ) -> None:
        raise NotImplementedError
