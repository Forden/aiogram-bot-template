class BaseAiogramBotTemplateError(Exception):
    """
    Base exception for all Aiogram bot template errors
    """


class DetailedAiogramBotTemplateError(BaseAiogramBotTemplateError):
    """
    Base exception for all Aiogram bot template errors with detailed message
    """

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        message = self.message
        return message

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self}')"
