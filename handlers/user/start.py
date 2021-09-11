from aiogram import types
from utils.db.mongo import BaseMongo
from loguru import logger

async def bot_start(msg: types.Message):

    db = BaseMongo.get_data_base()

    user = await db.Users.find_one({
        "telegram_id": msg.from_user.id
    })

    if user:
        return await msg.answer("Еще раз привет!")

    result = await db.Users.insert_one({
        "telegram_id": msg.from_user.id,
        "first_name": msg.from_user.first_name,
        "last_name": msg.from_user.last_name,
        "username": msg.from_user.username
    })
    logger.info(
        f"/start user_id={msg.from_user.id} insert_one result={result.acknowledged} id={result.inserted_id}")

    await msg.answer(f'Привет, {msg.from_user.full_name}!')
