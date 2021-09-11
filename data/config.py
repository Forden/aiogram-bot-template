from pathlib import Path

PORT = 8877
BOT_TOKEN = '' # Нужно добавить!
WEBHOOK_PATH = f'/tg/webhooks/bot/{BOT_TOKEN}'

LOGS_BASE_PATH = str(Path(__file__).parent.parent / 'logs')

admins = []

ip = {
    'db':    '',
    'redis': '',
}

mysql_info = {
    'host':     ip['db'],
    'user':     '',
    'password': '',
    'db':       '',
    'maxsize':  5,
    'port':     3306,
}

redis = {
    'host':     ip['redis'],
    'password': ''
}

mongo = {
    'hostname':  '127.0.0.1',
    'password': 'root',
    'username':  'example',
    'port': 27017,
    'database': 'telegram_bot'
}
