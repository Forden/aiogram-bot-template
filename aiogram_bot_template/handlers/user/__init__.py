from aiogram import Router
from aiogram.filters import CommandStart, StateFilter

from aiogram_bot_template import states
from aiogram_bot_template.filters import ChatTypeFilter, TextFilter

from . import start


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(
        start.start,
        TextFilter("🏠В главное меню"),
        StateFilter(states.user.UserMainMenu.menu),
    )

    return user_router
