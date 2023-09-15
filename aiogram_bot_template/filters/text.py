from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class TextFilter(BaseFilter):
    def __init__(self, text: str | list[str]):
        if isinstance(text, str):
            self.text = [text]
        else:
            self.text = text

    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, Message):
            txt = obj.text or obj.caption
            return any(i == txt for i in self.text)
        elif isinstance(obj, CallbackQuery):
            return obj.data in self.text
        return False
