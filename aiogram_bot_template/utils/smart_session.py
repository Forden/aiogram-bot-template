import asyncio
import time
from typing import Any, Optional

import structlog.typing
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramRetryAfter,
    TelegramServerError,
)
from aiogram.methods.base import TelegramMethod, TelegramType


class StructLogAiogramAiohttpSessions(AiohttpSession):
    def __init__(self, logger: structlog.typing.FilteringBoundLogger, **kwargs: Any):
        super().__init__(**kwargs)
        self._logger = logger

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = None,
    ) -> TelegramType:
        req_logger = self._logger.bind(
            bot=bot.token,
            method=method.model_dump(exclude_none=True, exclude_unset=True),
            timeout=timeout,
            api=self.api,
            url=self.api.api_url(bot.token, method.__api_method__),
        )
        st = time.monotonic()
        req_logger.debug("Making request to API")
        try:
            res = await super().make_request(bot, method, timeout)
        except Exception as e:
            req_logger.error(
                "API error",
                error=e,
                time_spent_ms=(time.monotonic() - st) * 1000,
            )
            raise e
        req_logger.debug(
            "API response",
            response=(
                res.model_dump(exclude_none=True, exclude_unset=True)
                if hasattr(res, "model_dump")
                else res
            ),
            time_spent_ms=(time.monotonic() - st) * 1000,
        )
        return res


class SmartAiogramAiohttpSession(StructLogAiogramAiohttpSessions):
    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: Optional[int] = None,
    ) -> TelegramType:
        attempt = 0
        while True:
            attempt += 1
            try:
                res = await super().make_request(bot, method, timeout)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except (RestartingTelegram, TelegramServerError):
                if attempt > 6:
                    sleepy_time = 64
                else:
                    sleepy_time = 2**attempt
                await asyncio.sleep(sleepy_time)
            except Exception as e:
                raise e
            else:
                return res
