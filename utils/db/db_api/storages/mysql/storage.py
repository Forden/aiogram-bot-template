import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import aiomysql
from loguru import logger

from data import config
from ..basestorage.storage import RawConnection

T = TypeVar("T")


# noinspection DuplicatedCode
class MysqlConnection(RawConnection):
    connection_pool = None

    @staticmethod
    async def __make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            retries_count: int = 5
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        if MysqlConnection.connection_pool is None:
            MysqlConnection.connection_pool = await aiomysql.create_pool(**config.mysql_info)
        async with MysqlConnection.connection_pool.acquire() as conn:
            conn: aiomysql.Connection = conn
            async with conn.cursor(aiomysql.DictCursor) as cur:
                cur: aiomysql.DictCursor = cur
                for i in range(retries_count):
                    try:
                        if isinstance(params, list):
                            await cur.executemany(sql, params)
                        else:
                            await cur.execute(sql, params)
                    except (aiomysql.OperationalError, aiomysql.InternalError) as e:
                        logger.error(f'Found error [{e}]  [{sql}] [{params}] retrying [{i}/{retries_count}]')
                        if 'Deadlock found' in str(e):
                            await asyncio.sleep(1)
                    else:
                        break
                if fetch:
                    if mult:
                        r = await cur.fetchall()
                    else:
                        r = await cur.fetchone()
                    return r
                else:
                    await conn.commit()

    @staticmethod
    def _convert_to_model(data: Optional[dict], model: Type[T]) -> Optional[T]:
        if data is not None:
            return model(**data)
        else:
            return None

    @staticmethod
    async def _make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            model_type: Type[T] = None
    ) -> Optional[Union[List[T], T]]:
        raw = await MysqlConnection.__make_request(sql, params, fetch, mult)
        if raw is None:
            if mult:
                return []
            else:
                return None
        else:
            if mult:
                if model_type is not None:
                    return [MysqlConnection._convert_to_model(i, model_type) for i in raw]
                else:
                    return list(raw)
            else:
                if model_type is not None:
                    return MysqlConnection._convert_to_model(raw, model_type)
                else:
                    return raw
