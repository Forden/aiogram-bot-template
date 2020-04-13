import asyncio
from typing import Optional, Dict, Any, Union, List

import aiomysql

from data import config


class RawConnection:
    connection_pool = None

    @staticmethod
    async def _make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            retries_count: int = 5
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        if RawConnection.connection_pool is None:
            RawConnection.connection_pool = await aiomysql.create_pool(**config.mysql_info)
        async with RawConnection.connection_pool.acquire() as conn:
            conn: aiomysql.Connection = conn
            async with conn.cursor(aiomysql.DictCursor) as cur:
                cur: aiomysql.DictCursor = cur
                for i in range(retries_count):
                    try:
                        if isinstance(params, list):
                            await cur.executemany(sql, params)
                        else:
                            await cur.execute(sql, params)
                    except aiomysql.OperationalError as e:
                        if 'Deadlock found' in str(e):
                            await asyncio.sleep(1)
                    except aiomysql.InternalError as e:
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
