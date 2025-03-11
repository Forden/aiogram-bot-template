from collections.abc import Sequence
from types import MappingProxyType

from aiogram.types import (
    KeyboardButton,
    KeyboardButtonPollType,
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from aiogram_bot_template import exceptions
from aiogram_bot_template.keyboards.keyboard_utils import schema_generator

POSSIBLE_BUTTON_PROPERTIES_VALUES = (  # https://core.telegram.org/bots/api#keyboardbutton
    str
    | bool
    | KeyboardButtonPollType
    | KeyboardButtonRequestUsers
    | KeyboardButtonRequestChat
    | WebAppInfo
)
POSSIBLE_INPUT_ACTIONS_TYPES = str | dict[str, POSSIBLE_BUTTON_PROPERTIES_VALUES]


class DefaultConstructor:
    aliases = MappingProxyType(
        {
            "contact": "request_contact",
            "location": "request_location",
            "poll": "request_poll",
        },
    )
    required_properties = ("text",)
    additional_properties = (
        "request_contact",
        "request_location",
        "request_poll",
        "request_users",
        "request_chat",
        "web_app",
    )
    possible_properties = (*required_properties, *additional_properties)
    max_additional_properties = 1
    max_possible_properties = len(required_properties) + max_additional_properties

    @staticmethod
    def _create_kb(  # noqa: PLR0913
        actions: Sequence[POSSIBLE_INPUT_ACTIONS_TYPES],
        schema: Sequence[int],
        *,
        resize_keyboard: bool = True,
        selective: bool = False,
        one_time_keyboard: bool = False,
        is_persistent: bool = True,
    ) -> ReplyKeyboardMarkup:
        btns: list[KeyboardButton] = []
        # noinspection DuplicatedCode
        for i in actions:
            data: dict[str, POSSIBLE_BUTTON_PROPERTIES_VALUES] = {}
            if isinstance(i, str):
                data = {"text": i}
            elif isinstance(i, dict):
                cur_action: dict[str, POSSIBLE_BUTTON_PROPERTIES_VALUES] = {**i}
                data = {}
                for k, v in DefaultConstructor.aliases.items():
                    if k in cur_action:
                        cur_action[v] = cur_action[k]
                        del cur_action[k]
                for cur_action_k, cur_action_v in cur_action.items():
                    if cur_action_k not in DefaultConstructor.possible_properties:
                        raise exceptions.UnknownKeyboardButtonPropertyError(
                            unknown_property=cur_action_k,
                            property_value=cur_action_v,
                            known_properties=DefaultConstructor.possible_properties,
                        )
                    if len(data) >= DefaultConstructor.max_possible_properties:
                        raise exceptions.TooManyArgsToCreateButtonError(
                            provided_args=list(data.keys()),
                            max_args_amount=DefaultConstructor.max_possible_properties,
                        )
                    data[cur_action_k] = cur_action_v
                if not all(
                    added_property in data
                    for added_property in DefaultConstructor.required_properties
                ):
                    raise exceptions.NotEnoughArgsToCreateButtonError(
                        provided_args=list(data.keys()),
                        required_args=DefaultConstructor.required_properties,
                    )
            else:
                raise TypeError("unknown action type")  # noqa: TRY003, EM101
            btns.append(KeyboardButton(**data))  # type:ignore[arg-type]
        kb = ReplyKeyboardMarkup(
            resize_keyboard=resize_keyboard,
            selective=selective,
            one_time_keyboard=one_time_keyboard,
            is_persistent=is_persistent,
            keyboard=schema_generator.create_keyboard_layout(btns, schema),
        )
        return kb
