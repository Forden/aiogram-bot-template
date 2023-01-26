import logging
from typing import List, Tuple

import aiojobs as aiojobs
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode
from aiohttp import web

from data import config


async def create_db_connections(dp: Dispatcher):
    db_pool = await asyncpg.create_pool(**config.POSTGRES_CREDS, min_size=1, max_size=3)
    dp['pg_pool'] = db_pool


# noinspection PyUnusedLocal
async def on_startup(app: web.Application):
    logger = logging.getLogger('bot')
    import middlewares
    import filters
    import handlers
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    logger.info(f'Configure Webhook URL to: {config.WEBHOOK_URL}')
    await dp.bot.set_webhook(config.WEBHOOK_URL, allowed_updates=types.AllowedUpdates.all())


async def on_shutdown(app: web.Application):
    app_bot: Bot = app['bot']
    await app_bot.close()


async def init() -> web.Application:
    import web_handlers
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

    web.run_app(init())
