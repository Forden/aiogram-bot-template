from typing import Tuple

from aiogram import Bot
from aiohttp import web
from aiohttp_healthcheck import HealthCheck
from loguru import logger


async def health_check() -> Tuple[bool, str]:
    return True, 'Server alive'


async def check_webhook() -> Tuple[bool, str]:
    from data import config
    bot: Bot = health_app['bot']

    webhook = await bot.get_webhook_info()
    if webhook.url and webhook.url == config.WEBHOOK_URL:
        return True, f'Webhook configured. Pending updates count {webhook.pending_update_count}'
    else:
        logger.error('Configured wrong webhook URL {webhook}', webhook=webhook.url)
        return False, 'Configured invalid webhook URL'


health_app = web.Application()
health = HealthCheck()
health.add_check(health_check)
health.add_check(check_webhook)
health_app.add_routes([web.get('/check', health)])
