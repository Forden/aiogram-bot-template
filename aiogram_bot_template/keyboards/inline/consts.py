from types import MappingProxyType
from typing import TypeVar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackGame,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LoginUrl,
)

from aiogram_bot_template.keyboards.keyboard_utils import schema_generator

A = TypeVar("A", bound=type[CallbackData])


class InlineConstructor:
    aliases = MappingProxyType({"cb": "callback_data"})
    available_properities = (
        "text",
        "callback_data",
        "url",
        "login_url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "pay",
    )
    properties_amount = 2

    @staticmethod
    def _create_kb(
        actions: list[
            dict[
                str,
                str | bool | A | LoginUrl | CallbackGame,
            ]
        ],
        schema: list[int],
    ) -> InlineKeyboardMarkup:
        btns: list[InlineKeyboardButton] = []
        # noinspection DuplicatedCode
        for a in actions:
            data: dict[
                str,
                str | bool | A | LoginUrl | CallbackGame,
            ] = {}
            for k, v in InlineConstructor.aliases.items():
                if k in a:
                    a[v] = a[k]
                    del a[k]
            for k in a:
                if k in InlineConstructor.available_properities:
                    if len(data) < InlineConstructor.properties_amount:
                        data[k] = a[k]
                    else:
                        break
            if "callback_data" in data and isinstance(
                data["callback_data"],
                CallbackData,
            ):
                data["callback_data"] = data["callback_data"].pack()
            if "pay" in data:
                if len(btns) != 0 and data["pay"]:
                    msg = "Платежная кнопка должна идти первой в клавиатуре"
                    raise ValueError(msg)
                data["pay"] = a["pay"]
            if len(data) != InlineConstructor.properties_amount:
                msg = "Недостаточно данных для создания кнопки"
                raise ValueError(msg)
            btns.append(InlineKeyboardButton(**data))  # type: ignore
        kb = InlineKeyboardMarkup(
            inline_keyboard=schema_generator.create_keyboard_layout(btns, schema),
        )
        return kb
