from typing import Any, Optional, Type, TypeVar

import asyncpg
import structlog

from ..basestorage.storage import RawConnection

T = TypeVar("T")


class PostgresConnection(RawConnection):
    def __init__(
        self,
        connection_poll: asyncpg.Pool,
        logger: structlog.typing.FilteringBoundLogger,
    ):
        self._pool = connection_poll

        self._logger = logger

    async def _fetch(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]],
        model_type: Type[T],
    ) -> list[T]:
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        con: asyncpg.Connection
        async with self._pool.acquire() as con:
            try:
                if params is not None:
                    raw = await con.fetch(sql, *params)
                else:
                    raw = await con.fetch(sql)
            except Exception as e:
                # change to appropriate error handling
                request_logger = request_logger.bind(error=e)
                request_logger.error(f"{e}")
            else:
                if raw:
                    return [_convert_to_model(i, model_type) for i in raw]
                else:
                    return []
        return []

    async def _fetchrow(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]],
        model_type: Type[T],
    ) -> Optional[T]:
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        con: asyncpg.Connection
        async with self._pool.acquire() as con:
            try:
                if params is not None:
                    raw = await con.fetchrow(sql, *params)
                else:
                    raw = await con.fetchrow(sql)
            except Exception as e:
                # change to appropriate error handling
                request_logger = self._logger.bind(error=e)
                request_logger.error(f"{e}")
            else:
                if raw is not None:
                    return _convert_to_model(raw, model_type)
        return None

    async def _execute(
        self, sql: str, params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]]
    ) -> None:
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        con: asyncpg.Connection
        async with self._pool.acquire() as con:
            try:
                if params is not None:
                    if isinstance(params, list):
                        await con.executemany(sql, params)
                    else:
                        await con.execute(sql, *params)
                else:
                    await con.execute(sql)
            except Exception as e:
                # change to appropriate error handling
                request_logger = request_logger.bind(error=e)
                request_logger.error(f"{e}")


def _convert_to_model(data: asyncpg.Record, model: Type[T]) -> T:
    return model(**data)
