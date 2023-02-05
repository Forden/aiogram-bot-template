import time

import structlog.typing
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

HANDLED_STR = ['Unhandled', 'Handled']


class StructLoggingMiddleware(BaseMiddleware):
    def __init__(self, logger: structlog.typing.FilteringBoundLogger, logger_init_values: dict):
        self.logger = logger
        self.logger_init_values = logger_init_values
        super(StructLoggingMiddleware, self).__init__()

    def check_timeout(self, obj):
        start = obj.conf.get('_start', None)
        if start:
            del obj.conf['_start']
            return round((time.time() - start) * 1000)
        return -1

    async def on_pre_process_update(self, update: types.Update, data: dict):
        self.logger.new(**self.logger_init_values)
        update.conf['_start'] = time.time()
        self.logger = self.logger.bind(update_id=update.update_id)
        self.logger.debug(f"Received update")

    async def on_post_process_update(self, update: types.Update, result, data: dict):
        timeout = self.check_timeout(update)
        if timeout > 0:
            self.logger = self.logger.bind(spent_time_ms=timeout)
            self.logger.info("Processed update")

    async def on_pre_process_message(self, message: types.Message, data: dict):
        self.logger = self.logger.bind(
            message_id=message.message_id, chat_type=message.chat.type, chat_id=message.chat.id,
            user_id=message.from_user.id
        )
        if message.text:
            self.logger = self.logger.bind(
                text=message.text, entities=message.entities
            )
        if message.video:
            self.logger = self.logger.bind(
                caption=message.caption, caption_entities=message.caption_entities,
                video_id=message.video.file_id, video_unique_id=message.video.file_unique_id
            )
        if message.photo:
            self.logger = self.logger.bind(
                caption=message.caption, caption_entities=message.caption_entities,
                photo_id=message.photo[-1].file_id, photo_unique_id=message.photo[-1].file_unique_id
            )
        self.logger.debug("Received message")

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        self.logger = self.logger.bind(process_result=True)
        self.logger.info(f"Handled message")

    async def on_pre_process_callback_query(self, c: types.CallbackQuery, data: dict):
        self.logger = self.logger.bind(
            callback_query_id=c.id, callback_data=c.data,
            user_id=c.from_user.id, inline_message_id=c.inline_message_id, chat_instance=c.chat_instance,
            message_id=c.message.message_id, chat_type=c.message.chat.type, chat_id=c.message.chat.id,
        )
        self.logger.debug("Received callback query")

    async def on_post_process_callback_query(self, c: types.CallbackQuery, results, data: dict):
        self.logger = self.logger.bind(process_result=True)
        self.logger.info(f"Handled callback query")
