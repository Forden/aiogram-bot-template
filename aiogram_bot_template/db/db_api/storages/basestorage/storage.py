from typing import Optional, Type, TypeVar

T = TypeVar("T")


class RawConnection:
    async def _fetch(
        self, sql: str, params: Optional[tuple | list[tuple]], model_type: Type[T]
    ) -> Optional[list[T]]:
        raise NotImplementedError

    async def _fetchrow(
        self, sql: str, params: Optional[tuple | list[tuple]], model_type: Type[T]
    ) -> Optional[T]:
        raise NotImplementedError

    async def _execute(self, sql: str, params: Optional[tuple | list[tuple]]):
        raise NotImplementedError
