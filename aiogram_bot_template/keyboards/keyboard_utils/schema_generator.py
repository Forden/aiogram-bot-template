from collections.abc import Sequence
from typing import TypeVar

from aiogram_bot_template import exceptions

T = TypeVar("T")


def create_keyboard_layout(buttons: Sequence[T], count: Sequence[int]) -> list[list[T]]:
    if sum(count) != len(buttons):
        raise exceptions.WrongKeyboardSchemaError(
            schema_size=sum(count),
            buttons_count=len(buttons),
        )
    tmplist: list[list[T]] = []
    btn_number = 0
    for a in count:
        tmplist.append([])
        for _ in range(a):
            tmplist[-1].append(buttons[btn_number])
            btn_number += 1
    return tmplist
