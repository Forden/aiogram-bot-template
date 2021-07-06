from typing import Dict, List, Union

from aiogram.types import KeyboardButton, KeyboardButtonPollType, ReplyKeyboardMarkup

from ..keyboard_utils import schema_generator


class DefaultConstructor:
    aliases = {
        'contact':  'request_contact',
        'location': 'request_location',
        'poll':     'request_poll'
    }
    available_properities = ['text', 'request_contact', 'request_location', 'request_poll']
    properties_amount = 1

    @staticmethod
    def _create_kb(
            actions: List[Union[str, Dict[str, Union[str, bool, KeyboardButtonPollType]]]],
            schema: List[int],
            resize_keyboard: bool = True,
            selective: bool = False,
            one_time_keyboard: bool = False
    ) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(
            resize_keyboard=resize_keyboard, selective=selective, one_time_keyboard=one_time_keyboard
        )
        kb.row_width = max(schema)
        btns = []
        # noinspection DuplicatedCode
        for a in actions:
            if isinstance(a, str):
                a = {'text': a}
            data: Dict[str, Union[str, bool, KeyboardButtonPollType]] = {}
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
                raise ValueError('Недостаточно данных для создания кнопки')
            btns.append(KeyboardButton(**data))
        kb.keyboard = schema_generator.create_keyboard_layout(btns, schema)
        return kb
