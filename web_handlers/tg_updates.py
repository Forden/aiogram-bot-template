from aiogram import Bot, Dispatcher, types
from aiohttp import web

tg_updates_app = web.Application()


async def proceed_update(req: web.Request):
    upds = [types.Update(**(await req.json()))]
    Bot.set_current(req.app['bot'])
    Dispatcher.set_current(req.app['dp'])
    await req.app['dp'].process_updates(upds)


async def execute(req: web.Request) -> web.Response:
    await req.app['scheduler'].spawn(proceed_update(req))
    return web.Response()


tg_updates_app.add_routes([web.post('/bot/{token}', execute)])
