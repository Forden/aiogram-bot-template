from types import MappingProxyType

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackGame,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LoginUrl,
    SwitchInlineQueryChosenChat,
    WebAppInfo,
)

from aiogram_bot_template import exceptions
from aiogram_bot_template.keyboards.keyboard_utils import schema_generator

POSSIBLE_BUTTON_PROPERTIES_VALUES = (  # https://core.telegram.org/bots/api#inlinekeyboardbutton
    str
    | WebAppInfo
    | LoginUrl
    | SwitchInlineQueryChosenChat
    | CallbackGame
    | bool
    | CallbackData  # aiogram callback factory
)
POSSIBLE_INPUT_ACTIONS_TYPES = dict[str, POSSIBLE_BUTTON_PROPERTIES_VALUES]


class InlineConstructor:
    aliases = MappingProxyType(
        {
            "cb": "callback_data",
        },
    )
    required_properties = ("text",)
    additional_properties = (
        "callback_data",
        "url",
        "web_app",
        "login_url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "pay",
    )
    possible_properties = (*required_properties, *additional_properties)
    max_additional_properties = 1
    max_possible_properties = len(required_properties) + max_additional_properties

    @staticmethod
    def _create_kb(  # noqa: C901
        actions: list[POSSIBLE_INPUT_ACTIONS_TYPES],
        schema: list[int],
    ) -> InlineKeyboardMarkup:
        btns: list[InlineKeyboardButton] = []
        # noinspection DuplicatedCode
        for cur_action in actions:
            data: dict[str, POSSIBLE_BUTTON_PROPERTIES_VALUES] = {}
            for k, v in InlineConstructor.aliases.items():
                if k in cur_action:
                    cur_action[v] = cur_action[k]
                    del cur_action[k]
            for k in cur_action:
                if k not in InlineConstructor.possible_properties:
                    raise exceptions.UnknownKeyboardButtonPropertyError(
                        unknown_property=k,
                        property_value=cur_action[k],
                        known_properties=InlineConstructor.possible_properties,
                    )
                if len(data) >= InlineConstructor.max_possible_properties:
                    raise exceptions.TooManyArgsToCreateButtonError(
                        provided_args=list(data.keys()),
                        max_args_amount=InlineConstructor.max_possible_properties,
                    )
                data[k] = cur_action[k]
            if not all(
                added_property in data
                for added_property in InlineConstructor.required_properties
            ):
                raise exceptions.NotEnoughArgsToCreateButtonError(
                    provided_args=list(data.keys()),
                    required_args=InlineConstructor.required_properties,
                )
            if isinstance(data["callback_data"], CallbackData):
                data["callback_data"] = data["callback_data"].pack()
            if "pay" in data:
                if len(btns) != 0 and data["pay"]:
                    raise exceptions.PaymentButtonMustBeFirstError
                data["pay"] = cur_action["pay"]
            btns.append(InlineKeyboardButton(**data))  # type:ignore[arg-type]
        kb = InlineKeyboardMarkup(
            inline_keyboard=schema_generator.create_keyboard_layout(btns, schema),
        )
        return kb
