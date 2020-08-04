from typing import List, Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def create_keyboard_layout(
        buttons: List[Union[InlineKeyboardButton, KeyboardButton]],
        count: List[int]
) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
    if sum(count) != len(buttons):
        raise ValueError('Количество кнопок не совпадает со схемой')
    tmplist = []
    for a in count:
        tmplist.append([])
        for _ in range(a):
            tmplist[-1].append(buttons.pop(0))
    return tmplist
