import time
from collections.abc import Awaitable, Callable
from contextlib import suppress
from types import TracebackType
from typing import Any

import structlog.typing
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

HANDLED_STR = ["Unhandled", "Handled"]


class UpdateLoggingContextManager:
    def __init__(
        self,
        logger: structlog.typing.FilteringBoundLogger,
        event: Update,
    ) -> None:
        self.event = event
        self.logger = logger.bind(update_id=self.event.update_id)

    def _fill_logger(self) -> None:
        if self.event.callback_query:
            c = self.event.callback_query
            self.logger = self.logger.bind(
                callback_query_id=c.id,
                callback_data=c.data,
                user_id=c.from_user.id,
                inline_message_id=c.inline_message_id,
                chat_instance=c.chat_instance,
            )
            if c.message is not None:
                self.logger = self.logger.bind(
                    message_id=c.message.message_id,
                    chat_type=c.message.chat.type,
                    chat_id=c.message.chat.id,
                )
        elif (
            self.event.message
            or self.event.edited_message
            or self.event.channel_post
            or self.event.edited_channel_post
        ):
            if self.event.message:
                message = self.event.message
            elif self.event.edited_message:
                message = self.event.edited_message
            elif self.event.channel_post:
                message = self.event.channel_post
            elif self.event.edited_channel_post:
                message = self.event.edited_channel_post
            else:
                msg = "Unexpected entry in logging for event message"
                raise RuntimeError(msg)
            self.logger = self.logger.bind(
                message_id=message.message_id,
                chat_type=message.chat.type,
                chat_id=message.chat.id,
                date=message.date,
                content_type=message.content_type,
            )
            if message.from_user is not None:
                self.logger = self.logger.bind(user_id=message.from_user.id)
            if message.sender_chat is not None:
                self.logger = self.logger.bind(
                    sender_chat_id=message.sender_chat.id,
                )
            if message.text:
                self.logger = self.logger.bind(text=message.text)
                if message.entities:
                    self.logger = self.logger.bind(
                        caption_entities=[
                            i.model_dump(exclude_none=True, exclude_unset=True)
                            for i in message.entities
                        ],
                    )
            elif message.video:
                self.logger = self.logger.bind(
                    video_id=message.video.file_id,
                    video_unique_id=message.video.file_unique_id,
                )
            elif message.photo:
                best_photosize = max(message.photo, key=lambda x: x.width * x.height)
                self.logger = self.logger.bind(
                    photo_id=best_photosize.file_id,
                    photo_unique_id=best_photosize.file_unique_id,
                )
            if message.caption:
                self.logger = self.logger.bind(caption=message.caption)
                if message.caption_entities:
                    self.logger = self.logger.bind(
                        caption_entities=[
                            i.model_dump(exclude_none=True, exclude_unset=True)
                            for i in message.caption_entities
                        ],
                    )
        elif self.event.chat_join_request:
            req = self.event.chat_join_request
            self.logger = self.logger.bind(
                chat_id=req.chat.id,
                chat_type=req.chat.type,
                user_id=req.from_user.id,
                user_chat_id=req.user_chat_id,
                date=req.date,
                bio=req.bio,
            )
            if req.invite_link:
                self.logger = self.logger.bind(
                    invite_link=req.invite_link.model_dump(
                        exclude_none=True,
                        exclude_unset=True,
                    ),
                )
        elif self.event.chat_member:
            upd = self.event.chat_member
            self.logger = self.logger.bind(
                user_id=upd.from_user.id,
                chat_id=upd.chat.id,
                chat_type=upd.chat.type,
                old_state=upd.old_chat_member.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                ),
                new_state=upd.new_chat_member.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                ),
                via_chat_folder_invite_link=bool(upd.via_chat_folder_invite_link),
            )
            if upd.invite_link:
                self.logger = self.logger.bind(
                    invite_link=upd.invite_link.model_dump(
                        exclude_none=True,
                        exclude_unset=True,
                    ),
                )
        elif self.event.inline_query:
            query = self.event.inline_query
            self.logger = self.logger.bind(
                query_id=query.id,
                user_id=query.from_user.id,
                query=query.query,
                offset=query.offset,
                chat_type=query.chat_type,
                location=query.location,
            )
        elif self.event.my_chat_member:
            upd = self.event.my_chat_member
            self.logger = self.logger.bind(
                user_id=upd.from_user.id,
                chat_id=upd.chat.id,
                chat_type=upd.chat.type,
                old_state=upd.old_chat_member.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                ),
                new_state=upd.new_chat_member.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                ),
            )
        elif self.event.poll:
            poll = self.event.poll
            self.logger = self.logger.bind(
                poll_id=poll.id,
                question=poll.question,
                options=[
                    i.model_dump(exclude_none=True, exclude_unset=True)
                    for i in poll.options
                ],
                total_voter_count=poll.total_voter_count,
                is_closed=bool(poll.is_closed),
                is_anonymous=bool(poll.is_anonymous),
                type=poll.type,
                allows_multiple_answers=bool(poll.allows_multiple_answers),
            )
            if poll.correct_option_id:
                self.logger = self.logger.bind(correct_option_id=poll.correct_option_id)
            if poll.explanation:
                self.logger = self.logger.bind(explanation=poll.explanation)
                if poll.explanation_entities:
                    self.logger = self.logger.bind(
                        explanation_entities=[
                            i.model_dump(exclude_none=True, exclude_unset=True)
                            for i in poll.explanation_entities
                        ],
                    )
            if poll.open_period:
                self.logger = self.logger.bind(open_period=poll.open_period)
            if poll.close_date:
                self.logger = self.logger.bind(close_date=poll.close_date)

    async def __aenter__(self) -> None:
        self._started_processing_at = time.monotonic_ns()
        self._fill_logger()
        self.logger.debug(
            "Received {event_type}",
            extra={"event_type": self.event.event_type},
        )

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        self.logger.bind(
            process_result=True,
            spent_time_ms=(
                (time.monotonic_ns() - self._started_processing_at) * 1_000_000
            ),
        )
        self.logger.info(
            "Handled {event_type}",
            extra={"event_type": self.event.event_type},
        )


class StructLoggingMiddleware(BaseMiddleware):
    def __init__(
        self,
        logger: structlog.typing.FilteringBoundLogger,
    ) -> None:
        self.logger = logger
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        _started_processing_at = time.monotonic_ns()
        if not isinstance(event, Update):
            msg = "StructLoggingMiddleware can only work with updates"
            raise TypeError(msg)
        self._bind_loggers(event, data)
        async with UpdateLoggingContextManager(logger=self.logger, event=event):
            handler_result = await handler(event, data)
        return handler_result

    def _bind_loggers(self, event: Update, data: dict[str, Any]) -> None:
        update_id = event.update_id
        for possible_logger_name in [
            "business_logger",
            "aiogram_logger",
            "aiogram_session_logger",
            "db_logger",
            "cache_logger",
        ]:
            with suppress(Exception):  # Easier to ask for forgiveness than permission
                data[possible_logger_name] = data[possible_logger_name].bind(
                    update_id=update_id,
                )
