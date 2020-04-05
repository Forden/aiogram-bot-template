from aiogram import types


async def bot_start(msg: types.Message):
    await msg.answer(f'Привет, {msg.from_user.full_name}!')
