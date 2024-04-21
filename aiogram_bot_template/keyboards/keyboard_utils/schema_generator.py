from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def create_keyboard_layout(buttons: Sequence[T], count: Sequence[int]) -> list[list[T]]:
    if sum(count) != len(buttons):
        msg = "Количество кнопок не совпадает со схемой"  # noqa: RUF001
        raise ValueError(msg)
    tmplist: list[list[T]] = []
    btn_number = 0
    for a in count:
        tmplist.append([])
        for _ in range(a):
            tmplist[-1].append(buttons[btn_number])
            btn_number += 1
    return tmplist
