from typing import List, Tuple, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from . import utils


class InlineConstructor:
    @staticmethod
    def _create_kb(actions: List[Tuple[str, Dict[str, str], CallbackData]], schema: List[int]) -> InlineKeyboardMarkup:
        btns = []
        for a, b, c in actions:
            btns.append(
                InlineKeyboardButton(
                    text=a,
                    callback_data=c.new(**b)
                )
            )
        kb = utils.misc.arrange_inline_schema(btns, schema)
        return kb
