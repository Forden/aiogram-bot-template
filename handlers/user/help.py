from aiogram import types

from utils.misc import rate_limit


@rate_limit(5, 'help')
async def bot_help(msg: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку'
    ]
    await msg.answer('\n'.join(text))
