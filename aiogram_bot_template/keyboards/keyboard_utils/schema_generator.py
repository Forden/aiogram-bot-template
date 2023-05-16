from typing import Sequence, TypeVar

T = TypeVar("T")


def create_keyboard_layout(buttons: Sequence[T], count: Sequence[int]) -> list[list[T]]:
    if sum(count) != len(buttons):
        raise ValueError("Количество кнопок не совпадает со схемой")
    tmplist: list[list[T]] = []
    btn_number = 0
    for a in count:
        tmplist.append([])
        for _ in range(a):
            tmplist[-1].append(buttons[btn_number])
            btn_number += 1
    return tmplist
