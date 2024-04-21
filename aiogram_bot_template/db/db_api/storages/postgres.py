import json
import time
from typing import Any, TypeVar

import asyncpg
import orjson
import structlog

from .base import BaseConnection, MultipleQueryResults, SingleQueryResult

T = TypeVar("T")


class PostgresConnection(BaseConnection):
    CONNECTION_TYPES_CODES = (
        ("json", json.dumps, orjson.loads, "pg_catalog"),
        ("jsonb", json.dumps, orjson.loads, "pg_catalog"),
    )

    def __init__(
        self,
        connection_poll: asyncpg.Pool,
        logger: structlog.typing.FilteringBoundLogger,
    ) -> None:
        self._pool = connection_poll

        self._logger = logger

    async def apply_connection_types_codecs(
        self,
        connection: asyncpg.Connection,
    ) -> None:
        for typename, encoder, decoder, schema in self.CONNECTION_TYPES_CODES:
            await connection.set_type_codec(
                typename=typename,
                encoder=encoder,
                decoder=decoder,
                schema=schema,
            )

    async def _fetch(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: asyncpg.Connection | None = None,
    ) -> MultipleQueryResults:
        async def __fetch(
            connection: asyncpg.Connection,
            query: str,
            query_params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        ) -> Any:
            await self.apply_connection_types_codecs(connection)

            if params is not None:
                res = await connection.fetch(query, *query_params)
            else:
                res = await connection.fetch(query)
            return res

        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as local_con:
                    raw_result = await __fetch(local_con, sql, params)
            else:
                raw_result = await __fetch(con, sql, params)
        except Exception as e:
            # change to appropriate error handling
            request_logger = request_logger.bind(error=e)
            request_logger.exception("Error while making query")
            raise
        else:
            results = list(raw_result)
        finally:
            request_logger.debug(
                "Finished query to DB",
                spent_time_ms=(time.monotonic() - st) * 1000,
            )

        return MultipleQueryResults(results)

    async def _fetchrow(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: asyncpg.Connection | None = None,
    ) -> SingleQueryResult:
        async def __fetchrow(
            connection: asyncpg.Connection,
            query: str,
            query_params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        ) -> Any:
            await self.apply_connection_types_codecs(connection)

            if params is not None:
                res = await connection.fetchrow(query, *query_params)
            else:
                res = await connection.fetchrow(query)
            return res

        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")

        try:
            if con is None:
                async with self._pool.acquire() as local_con:
                    raw_result = await __fetchrow(local_con, sql, params)
            else:
                raw_result = await __fetchrow(con, sql, params)
        except Exception as e:
            # change to appropriate error handling
            request_logger = request_logger.bind(error=e)
            request_logger.exception("Error while making query")
            raise
        else:
            result = raw_result
        finally:
            request_logger.debug(
                "Finished query to DB",
                spent_time_ms=(time.monotonic() - st) * 1000,
            )

        return SingleQueryResult(result)

    async def _execute(
        self,
        sql: str,
        params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        con: asyncpg.Connection | None = None,
    ) -> None:
        async def __execute(
            connection: asyncpg.Connection,
            query: str,
            query_params: tuple[Any, ...] | list[tuple[Any, ...]] | None = None,
        ) -> None:
            await self.apply_connection_types_codecs(connection)

            if query_params is not None:
                if isinstance(query_params, list):
                    await connection.executemany(query, query_params)
                else:
                    await connection.execute(query, *query_params)
            else:
                await connection.execute(query)

        st = time.monotonic()
        request_logger = self._logger.bind(sql=sql, params=params)
        request_logger.debug("Making query to DB")
        try:
            if con is None:
                async with self._pool.acquire() as local_con:
                    await __execute(local_con, sql, params)
            else:
                await __execute(con, sql, params)
        except Exception as e:
            # change to appropriate error handling
            request_logger = self._logger.bind(error=e)
            request_logger.exception("Error while making query")
            raise
        finally:
            request_logger.debug(
                "Finished query to DB",
                spent_time_ms=(time.monotonic() - st) * 1000,
            )
