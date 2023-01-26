import asyncpg
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "channel_post"]

    def __init__(
            self,
            pool: asyncpg.Pool,
    ):
        super().__init__()
        self.pool = pool
        self.passing_map = {
        }

    async def pre_process(self, obj, data, *args):
        for k, v in self.passing_map.items():
            data[k] = v

    async def post_process(self, obj, data, *args):
        for k in self.passing_map:
            if k in data:
                del data[k]
