from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def arrange_inline_schema(buttons: List[InlineKeyboardButton], count: List[int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    btns = buttons
    kb.row_width = max(count)
    if sum(count) != len(buttons):
        raise ValueError('Количество кнопок не совпадает со схемой')
    tmplist = [[InlineKeyboardButton('') for _ in range(count[i])] for i in range(len(count))]
    for a in range(len(tmplist)):
        for b in range(len(tmplist[a])):
            tmplist[a][b] = btns.pop(0)
    kb.inline_keyboard = tmplist
    return kb
