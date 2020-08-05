from aiogram import Bot, Dispatcher, types
from aiohttp import web

from loguru import logger

tg_updates_app = web.Application()


async def execute(req: web.Request) -> web.Response:
    upds = [types.Update(**(await req.json()))]
    Bot.set_current(req.app['bot'])
    Dispatcher.set_current(req.app['dp'])
    try:
        await req.app['dp'].process_updates(upds)
    except Exception as e:
        logger.error(e)
    finally:
        return web.Response()


tg_updates_app.add_routes([web.post('/{token}', execute)])
