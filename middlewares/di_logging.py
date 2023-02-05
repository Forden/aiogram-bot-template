import structlog.typing
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

HANDLED_STR = ['Unhandled', 'Handled']


class StructLoggerMiddleware(BaseMiddleware):
    def __init__(self, logger: structlog.typing.FilteringBoundLogger, logger_init_values: dict):
        self.logger = logger
        self.logger_init_values = logger_init_values
        super(StructLoggerMiddleware, self).__init__()

    async def on_pre_process_update(self, update: types.Update, data: dict):
        self.logger = self.logger.new(**self.logger_init_values)
        self.logger = self.logger.bind(update_id=update.update_id)
        data['logger'] = self.logger

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data['logger'] = self.logger

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        del data['logger']

    async def on_pre_process_callback_query(self, c: types.CallbackQuery, data: dict):
        data['logger'] = self.logger

    async def on_post_process_callback_query(self, c: types.CallbackQuery, results, data: dict):
        del data['logger']