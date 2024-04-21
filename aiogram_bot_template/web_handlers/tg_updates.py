import secrets
from typing import Any, TYPE_CHECKING

import aiohttp.web
import orjson
from aiogram import Bot, Dispatcher, types
from aiohttp import web

from aiogram_bot_template.data import config

if TYPE_CHECKING:
    import aiojobs

tg_updates_app = web.Application()


async def process_update(
    upd: types.Update,
    bot: Bot,
    dp: Dispatcher,
    workflow_data: dict[str, Any],
) -> None:

    await dp.feed_webhook_update(bot, upd, **workflow_data)


async def execute(req: web.Request) -> web.Response:
    if not secrets.compare_digest(
        req.headers.get("X-Telegram-Bot-Api-Secret-Token", ""),
        config.MAIN_WEBHOOK_SECRET_TOKEN,
    ):
        raise aiohttp.web.HTTPNotFound
    if not secrets.compare_digest(req.match_info["bot_id"], config.BOT_ID):
        raise aiohttp.web.HTTPNotFound

    dp: Dispatcher = req.app["dp"]
    scheduler: aiojobs.Scheduler = req.app["scheduler"]
    if scheduler.pending_count > 100:
        raise web.HTTPTooManyRequests
    if scheduler.closed:
        raise web.HTTPServiceUnavailable(reason="Closed queue")
    await scheduler.spawn(
        process_update(
            types.Update(**(await req.json(loads=orjson.loads))),
            req.app["bot"],
            dp,
            {"dp": dp},
        ),
    )

    return web.Response()


tg_updates_app.add_routes(
    [web.post("/bot/{bot_id}", execute)],
)
