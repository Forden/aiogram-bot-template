import asyncio
from typing import Optional

import aioredis

from data import config

data_pool: Optional[aioredis.Redis] = None


async def create_pools():
    global data_pool
    data_pool = await aioredis.create_redis_pool(**config.redis, db=1)


class BaseRedis:
    def __init__(self, host: str, port: int = 6379, db: int = 0, password: str = ''):
        self.host = host
        self.port = port
        self.db = db
        self.password = password

        self._redis: Optional[aioredis.Redis] = None

    @property
    def closed(self):
        return not self._redis or self._redis.closed

    async def connect(self):
        if self.closed:
            self._redis = await aioredis.create_redis_pool((self.host, self.port), db=self.db, password=self.password,
                                                           timeout=10, encoding='utf8')

    async def disconnect(self):
        if not self.closed:
            self._redis.close()
            await self._redis.wait_closed()

    @property
    def redis(self) -> aioredis.Redis:
        if self.closed:
            if not self._redis:
                try:
                    await self.connect()
                except asyncio.TimeoutError:
                    raise TimeoutError('Redis connection timeout')
                else:
                    return self._redis
            else:
                raise RuntimeError("Redis connection is not opened")
        return self._redis


asyncio.get_event_loop().run_until_complete(create_pools())
