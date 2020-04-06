from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiohttp import web
from loguru import logger

import filters
import handlers
import middlewares
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(**config.aiogram_redis)
dp = Dispatcher(bot, storage=storage)


# noinspection PyUnusedLocal
async def on_startup(web_app: web.Application):
    filters.setup(dp)
    middlewares.setup(dp)
    handlers.errors.setup(dp)
    handlers.user.setup(dp)
    await dp.bot.delete_webhook()
    await dp.bot.set_webhook(config.WEBHOOK_URL)


async def execute(req: web.Request) -> web.Response:
    upds = [types.Update(**(await req.json()))]
    Bot.set_current(dp.bot)
    Dispatcher.set_current(dp)
    try:
        await dp.process_updates(upds)
    except Exception as e:
        logger.error(e)
    finally:
        return web.Response()


if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(on_startup)
    app.add_routes([web.post(config.WEBHOOK_PATH, execute)])
    web.run_app(app, port=5151, host='localhost')
