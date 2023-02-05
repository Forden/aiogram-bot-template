from aiogram import Dispatcher

from .db import DbMiddleware
from .di_logging import StructLoggerMiddleware
from .logging_middleware import StructLoggingMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(
        DbMiddleware(
            pool=dp['pg_pool'],
        )
    )
    dp.middleware.setup(
        StructLoggerMiddleware(logger=dp['business_logger'], logger_init_values=dp['business_logger_init'])
    )
    dp.middleware.setup(
        StructLoggingMiddleware(logger=dp['aiogram_logger'], logger_init_values=dp['aiogram_logger_init'])
    )
