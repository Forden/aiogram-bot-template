BOT_TOKEN = ''
BASE_URL = 'https://example.com'  # Webhook domain
WEBHOOK_PATH = f'/webhook/bot/{BOT_TOKEN}'
WEBHOOK_URL = f'{BASE_URL}{WEBHOOK_PATH}'

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

aiogram_redis = {
    'host':     ip['redis'],
    'password': ''
}

redis = {
    'address':  (ip['redis'], 6379),
    'password': '',
    'encoding': 'utf8'
}
