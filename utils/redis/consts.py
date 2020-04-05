import asyncio
from typing import Optional

import aioredis

from data import config

data_pool: Optional[aioredis.Redis] = None


async def create_pools():
    global data_pool
    data_pool = await aioredis.create_redis_pool(**config.redis, db=1)


asyncio.get_event_loop().run_until_complete(create_pools())
