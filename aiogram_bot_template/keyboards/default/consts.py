from collections.abc import Sequence
from types import MappingProxyType

from aiogram.types import KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup

from aiogram_bot_template.keyboards.keyboard_utils import schema_generator


class DefaultConstructor:

    aliases = MappingProxyType(
        {
            "contact": "request_contact",
            "location": "request_location",
            "poll": "request_poll",
        },
    )
    available_properities = (
        "text",
        "request_contact",
        "request_location",
        "request_poll",
        "request_user",
        "request_chat",
        "web_app",
    )
    properties_amount = 1

    @staticmethod
    def _create_kb(
        actions: Sequence[str | dict[str, str | bool | KeyboardButtonPollType]],
        schema: Sequence[int],
        resize_keyboard: bool = True,
        selective: bool = False,
        one_time_keyboard: bool = False,
        is_persistent: bool = True,
    ) -> ReplyKeyboardMarkup:
        btns: list[KeyboardButton] = []
        # noinspection DuplicatedCode
        for a in actions:
            if isinstance(a, str):
                a = {"text": a}  # noqa: PLW2901
            data: dict[str, str | bool | KeyboardButtonPollType] = {}
            for k, v in DefaultConstructor.aliases.items():
                if k in a:
                    a[v] = a[k]
                    del a[k]
            for k in a:
                if k in DefaultConstructor.available_properities:
                    if len(data) < DefaultConstructor.properties_amount:
                        data[k] = a[k]
                    else:
                        break
            if len(data) != DefaultConstructor.properties_amount:
                msg = "Недостаточно данных для создания кнопки"
                raise ValueError(msg)
            btns.append(KeyboardButton(**data))  # type: ignore
        kb = ReplyKeyboardMarkup(
            resize_keyboard=resize_keyboard,
            selective=selective,
            one_time_keyboard=one_time_keyboard,
            is_persistent=is_persistent,
            keyboard=schema_generator.create_keyboard_layout(btns, schema),
        )
        return kb
