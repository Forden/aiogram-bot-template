from aiogram import types, html
from aiogram.fsm.context import FSMContext

import states.user


async def start(msg: types.Message, state: FSMContext):
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>'
    ]
    await msg.answer("\n".join(m))
    await state.set_state(states.user.UserMainMenu.menu)
