from typing import List, Optional, Type, TypeVar, Union

import asyncpg
import structlog

from ..basestorage.storage import RawConnection

T = TypeVar("T")


class PostgresConnection(RawConnection):
    def __init__(
            self, connection_poll: asyncpg.Pool, logger: structlog.typing.FilteringBoundLogger, logger_init_values: dict
    ):
        self._pool = connection_poll

        self._logger = logger
        self._logger_init_values = logger_init_values

    async def __make_request(
            self,
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False
    ) -> Optional[Union[List[asyncpg.Record], asyncpg.Record]]:
        self._logger = self._logger.new(**self._logger_init_values)
        self._logger = self._logger.bind(sql=sql, params=params)
        self._logger.debug('Making query to DB')
        async with self._pool.acquire() as con:
            con: asyncpg.Connection
            try:
                if params is not None:
                    if fetch:
                        if mult:
                            r = await con.fetch(sql, *params)
                        else:
                            r = await con.fetchrow(sql, *params)
                        return r
                    else:
                        if isinstance(params, list):
                            await con.executemany(sql, params)
                        else:
                            await con.execute(sql, *params)
                else:
                    if fetch:
                        if mult:
                            r = await con.fetch(sql)
                        else:
                            r = await con.fetchrow(sql)
                        return r
                    else:
                        await con.execute(sql)
            except Exception as e:
                # change to appropriate error handling
                self._logger = self._logger.bind(error=e)
                self._logger.error(e)
                self._logger = self._logger.unbind('error')

    async def _make_request(
            self,
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            model_type: Type[T] = None
    ) -> Optional[Union[List[T], T, List[asyncpg.Record], asyncpg.Record]]:
        raw = await self.__make_request(sql, params, fetch, mult)
        if raw is None:
            if mult:
                return []
            else:
                return None
        else:
            if mult:
                if model_type is not None:
                    return [_convert_to_model(i, model_type) for i in raw]
                else:
                    return [i for i in raw]
            else:
                if model_type is not None:
                    return _convert_to_model(raw, model_type)
                else:
                    return raw


def _convert_to_model(data: Optional[asyncpg.Record], model: Type[T]) -> Optional[T]:
    if data is not None:
        return model(**data)
    else:
        return None
