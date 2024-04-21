import typing
from typing import Any, TypeVar

T = TypeVar("T")


class SingleQueryResult:
    def __init__(self, result: typing.Mapping[str, Any] | None) -> None:
        self._data = {**result} if result else None

    @property
    def data(self) -> dict[str, Any] | None:
        return self._data

    def convert(self, model: type[T]) -> T | None:
        return model(**self.data) if self._data else None


class MultipleQueryResults:
    def __init__(self, results: list[typing.Mapping[str, Any]]) -> None:
        self._data: list[dict[str, Any]] = [{**i} for i in results]

    @property
    def data(self) -> list[dict[str, Any]]:
        return self._data

    def convert(self, model: type[T]) -> list[T]:
        return [model(**i) for i in self._data]


class BaseConnection:
    async def _fetch(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: Any | None = None,
    ) -> MultipleQueryResults:
        raise NotImplementedError

    async def _fetchrow(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: Any | None = None,
    ) -> SingleQueryResult:
        raise NotImplementedError

    async def _execute(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: Any | None = None,
    ) -> None:
        raise NotImplementedError
