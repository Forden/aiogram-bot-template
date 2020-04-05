BOT_TOKEN = ''
WEBHOOK_URL = ''

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
