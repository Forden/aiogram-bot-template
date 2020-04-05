from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data import config


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        return message.from_user.id in config.admins
