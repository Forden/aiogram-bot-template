from typing import List, Tuple

import aiojobs as aiojobs
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiohttp import web
from loguru import logger
from pyngrok import ngrok
from data import config

WEBHOOK_HOST = ngrok.connect(config.PORT, bind_tls=True).public_url
WEBHOOK_URL = f"{WEBHOOK_HOST}{config.WEBHOOK_PATH}"

# noinspection PyUnusedLocal
async def on_startup(app: web.Application):
    import filters
    import handlers
    filters.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    logger.info('Configure Webhook URL to: {url}', url=WEBHOOK_URL)
    await dp.bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(app: web.Application):
    app_bot: Bot = app['bot']
    await app_bot.close()


async def init() -> web.Application:
    from utils.misc import logging
    import web_handlers
    logging.setup()
    scheduler = await aiojobs.create_scheduler()
    app = web.Application()
    subapps: List[Tuple[str, web.Application]] = [
        ('/tg/webhooks/', web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, validate_token=True)
    dp = Dispatcher(bot)
    web.run_app(init(), port=config.PORT)
