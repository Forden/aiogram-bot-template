import time
from typing import Any, Optional, TypeVar

import asyncpg
import structlog

from ..basestorage.storage import MultipleQueryResults, RawConnection, SingleQueryResult

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
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> MultipleQueryResults:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        raw_result = await con.fetch(sql, *params)
                    else:
                        raw_result = await con.fetch(sql)
            else:
                if params is not None:
                    raw_result = await con.fetch(sql, *params)
                else:
                    raw_result = await con.fetch(sql)
        except Exception as e:
            # change to appropriate error handling
            request_logger = request_logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        else:
            results = [i for i in raw_result]
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )

        return MultipleQueryResults(results)

    async def _fetchrow(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> SingleQueryResult:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")

        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        raw = await con.fetchrow(sql, *params)
                    else:
                        raw = await con.fetchrow(sql)
            else:
                if params is not None:
                    raw = await con.fetchrow(sql, *params)
                else:
                    raw = await con.fetchrow(sql)
        except Exception as e:
            # change to appropriate error handling
            request_logger = request_logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        else:
            result = raw
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )

        return SingleQueryResult(result)

    async def _execute(
        self,
        sql: str,
        params: Optional[tuple[Any, ...] | list[tuple[Any, ...]]] = None,
        con: Optional[asyncpg.Connection] = None,
    ) -> None:
        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as con:
                    if params is not None:
                        if isinstance(params, list):
                            await con.executemany(sql, params)
                        else:
                            await con.execute(sql, *params)
                    else:
                        await con.execute(sql)
            else:
                if params is not None:
                    if isinstance(params, list):
                        await con.executemany(sql, params)
                    else:
                        await con.execute(sql, *params)
                else:
                    await con.execute(sql)
        except Exception as e:
            # change to appropriate error handling
            request_logger = self._logger.bind(error=e)
            request_logger.error(f"Error while making query: {e}")
            raise e
        finally:
            request_logger.debug(
                "Finished query to DB", spent_time_ms=(time.monotonic() - st) * 1000
            )
