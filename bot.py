from typing import List, Tuple

import aiojobs as aiojobs
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode
from aiohttp import web

from data import config
from utils import misc


async def create_db_connections(dp: Dispatcher):
    db_pool = await asyncpg.create_pool(**config.POSTGRES_CREDS, min_size=1, max_size=3)
    dp['pg_pool'] = db_pool


def setup_logging(dp: Dispatcher):
    dp['business_logger'] = misc.setup_logger()
    dp['business_logger_init'] = {'type': 'business'}
    dp['aiogram_logger'] = misc.setup_logger()
    dp['aiogram_logger_init'] = {'type': 'aiogram'}


async def on_startup(app: web.Application):
    dp = app['dp']
    import middlewares
    import filters
    import handlers
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    webhook_logger = dp['aiogram_logger'].bind(webhook_url=config.WEBHOOK_URL)
    webhook_logger.info('Configured webhook')
    await dp.bot.set_webhook(config.WEBHOOK_URL, allowed_updates=types.AllowedUpdates.all())


async def on_shutdown(app: web.Application):
    app_bot: Bot = app['bot']
    await app_bot.close()


async def init(bot: Bot, dp: Dispatcher) -> web.Application:
    import web_handlers
    setup_logging(dp)
    await create_db_connections(dp)
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: List[Tuple[str, web.Application]] = [
        ('/tg/webhooks/', web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app['bot'] = bot
    app['dp'] = dp
    app['scheduler'] = scheduler
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, validate_token=True)
    storage = RedisStorage2(**config.REDIS_CREDS)
    dp = Dispatcher(bot, storage=storage)

    web.run_app(init(bot, dp), host='localhost', port=5005)
