from .consts import DefaultConstructor


class MainMenu(DefaultConstructor):
    @staticmethod
    def main_menu():
        schema = [2,2]
        actions = [
            'Список вакансий',
            'Приглашения на работу',
            'Результаты собеседований',
            'Настройки',
        ]
        return MainMenu._create_kb(actions, schema)

