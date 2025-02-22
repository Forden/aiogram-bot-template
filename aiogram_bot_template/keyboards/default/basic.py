import aiogram.types

from .consts import DefaultConstructor


class BasicButtons(DefaultConstructor):
    @staticmethod
    def back() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["◀️Назад"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1]
        btns = ["◀️Назад", "🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        schema.append(1)
        btns.append("✅Подтвердить")
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def skip(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["▶️Пропустить"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["✅Да"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def no(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2]
        btns = ["✅Да", "❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def ask_for_users(  # noqa: PLR0913
        text: str,
        *,
        request_id: int = 1,
        user_is_bot: bool | None = False,
        user_is_premium: bool | None = None,
        max_quantity: int | None = 1,
        request_name: bool | None = True,
        request_username: bool | None = True,
        request_photo: bool | None = True,
        add_back: bool = False,
        add_cancel: bool = True,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns: list[str | dict[str, str | aiogram.types.KeyboardButtonRequestUsers]] = [
            {
                "text": text,
                "request_users": aiogram.types.KeyboardButtonRequestUsers(
                    request_id=request_id,
                    user_is_bot=user_is_bot,
                    user_is_premium=user_is_premium,
                    max_quantity=max_quantity,
                    request_name=request_name,
                    request_username=request_username,
                    request_photo=request_photo,
                ),
            },
        ]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)  # type: ignore[arg-type]
