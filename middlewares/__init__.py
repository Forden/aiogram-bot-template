from aiogram import Dispatcher

from .db import DbMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(
        DbMiddleware(
            pool=dp['pg_pool'],
        )
    )
