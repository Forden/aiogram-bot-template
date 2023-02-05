from .consts import DefaultConstructor


class BasicButtons(DefaultConstructor):
    @staticmethod
    def back():
        schema = [1]
        btns = ['◀️Назад']
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def cancel():
        schema = [1]
        btns = ['🚫 Отмена']
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel():
        schema = [1, 1]
        btns = ['◀️Назад', '🚫 Отмена']
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(add_back: bool = False, add_cancel: bool = False):
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append('🚫 Отмена')
        schema.append(1)
        btns.append('✅Подтвердить')
        if add_back:
            schema.append(1)
            btns.append('◀️Назад')
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def skip(add_back: bool = False, add_cancel: bool = False):
        schema = [1]
        btns = ['▶️Пропустить']
        if add_back:
            schema.append(1)
            btns.append('◀️Назад')
        if add_cancel:
            schema.append(1)
            btns.append('🚫 Отмена')
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes(add_back: bool = False, add_cancel: bool = False):
        schema = [1]
        btns = ['✅Да']
        if add_back:
            schema.append(1)
            btns.append('◀️Назад')
        if add_cancel:
            schema.append(1)
            btns.append('🚫 Отмена')
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def no(add_back: bool = False, add_cancel: bool = False):
        schema = [1]
        btns = ['❌Нет']
        if add_back:
            schema.append(1)
            btns.append('◀️Назад')
        if add_cancel:
            schema.append(1)
            btns.append('🚫 Отмена')
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(add_back: bool = False, add_cancel: bool = False):
        schema = [2]
        btns = ['✅Да', '❌Нет']
        if add_back:
            schema.append(1)
            btns.append('◀️Назад')
        if add_cancel:
            schema.append(1)
            btns.append('🚫 Отмена')
        return BasicButtons._create_kb(btns, schema)
