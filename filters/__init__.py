from aiogram import Dispatcher

from .is_admin import AdminFilter


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
