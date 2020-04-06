from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from . import utils


class DefaultConstructor:
    @staticmethod
    def _create_kb(actions: List[str], schema: List[int]) -> ReplyKeyboardMarkup:
        btns = []
        for a in actions:
            btns.append(KeyboardButton(a))
        kb = utils.misc.arrange_default_schema(btns, schema)
        return kb
