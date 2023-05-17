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
        logger_init_values: dict[str, Any],
    ):
        self._pool = connection_poll

        self._logger = logger
        self._logger_init_values = logger_init_values

    async def _fetch(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]],
        model_type: Type[T],
    ) -> list[T]:
        self._logger = self._logger.new(**self._logger_init_values)
        self._logger = self._logger.bind(sql=sql, params=params)
        self._logger.debug("Making query to DB")
        con: asyncpg.Connection
        async with self._pool.acquire() as con:
            try:
                if params is not None:
                    raw = await con.fetch(sql, *params)
                else:
                    raw = await con.fetch(sql)
            except Exception as e:
                # change to appropriate error handling
                self._logger = self._logger.bind(error=e)
                self._logger.error(f"{e}")
                self._logger = self._logger.unbind("error")
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
        self._logger = self._logger.new(**self._logger_init_values)
        self._logger = self._logger.bind(sql=sql, params=params)
        self._logger.debug("Making query to DB")
        con: asyncpg.Connection
        async with self._pool.acquire() as con:
            try:
                if params is not None:
                    raw = await con.fetchrow(sql, *params)
                else:
                    raw = await con.fetchrow(sql)
            except Exception as e:
                # change to appropriate error handling
                self._logger = self._logger.bind(error=e)
                self._logger.error(f"{e}")
                self._logger = self._logger.unbind("error")
            else:
                if raw is not None:
                    return _convert_to_model(raw, model_type)
        return None

    async def _execute(
        self, sql: str, params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]]
    ) -> None:
        self._logger = self._logger.new(**self._logger_init_values)
        self._logger = self._logger.bind(sql=sql, params=params)
        self._logger.debug("Making query to DB")
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
                self._logger = self._logger.bind(error=e)
                self._logger.error(f"{e}")
                self._logger = self._logger.unbind("error")


def _convert_to_model(data: asyncpg.Record, model: Type[T]) -> T:
    return model(**data)
