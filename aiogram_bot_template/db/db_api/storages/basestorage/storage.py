from typing import Any, Optional, Type, TypeVar

T = TypeVar("T")


class RawConnection:
    async def _fetch(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]],
        model_type: Type[T],
    ) -> Optional[list[T]]:
        raise NotImplementedError

    async def _fetchrow(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]],
        model_type: Type[T],
    ) -> Optional[T]:
        raise NotImplementedError

    async def _execute(
        self, sql: str, params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]]
    ) -> None:
        raise NotImplementedError
