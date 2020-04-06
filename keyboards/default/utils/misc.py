from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def arrange_default_schema(buttons: List[KeyboardButton], count: List[int]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row_width = max(count)
    if sum(count) != len(buttons):
        raise ValueError('Количество кнопок не совпадает со схемой')
    tmplist = []
    for a in count:
        tmplist.append([])
        for _ in range(a):
            tmplist[-1].append(buttons.pop(0))
    kb.keyboard = tmplist
    return kb
