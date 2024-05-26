from collections.abc import Sequence

from .base import DetailedAiogramBotTemplateError


class UnknownKeyboardButtonPropertyError(DetailedAiogramBotTemplateError):
    def __init__(
        self,
        unknown_property: str,
        property_value: object,
        known_properties: Sequence[str],
    ) -> None:
        super().__init__(message="Unknown keyboard button property")
        self.unknown_property = unknown_property
        self.property_value = property_value
        self.known_properties = known_properties


class NotEnoughArgsToCreateButtonError(DetailedAiogramBotTemplateError):
    def __init__(
        self,
        provided_args: Sequence[str],
        required_args: Sequence[str],
    ) -> None:
        super().__init__(message="Not enough args to create button")
        self.provided_args = provided_args
        self.required_args = required_args


class TooManyArgsToCreateButtonError(DetailedAiogramBotTemplateError):
    def __init__(
        self,
        provided_args: Sequence[str],
        max_args_amount: int,
    ) -> None:
        super().__init__(message="Too many args to create button")
        self.provided_args = provided_args
        self.provided_args_amount = len(self.provided_args)
        self.max_args_amount = max_args_amount


class PaymentButtonMustBeFirstError(DetailedAiogramBotTemplateError):
    def __init__(self) -> None:
        super().__init__(message="Payment button must be first in keyboard")


class WrongKeyboardSchemaError(DetailedAiogramBotTemplateError):
    def __init__(self, schema_size: int, buttons_count: int) -> None:
        super().__init__(message="Schema size not equal to buttons count")
        self.schema_size = schema_size
        self.buttons_count = buttons_count
