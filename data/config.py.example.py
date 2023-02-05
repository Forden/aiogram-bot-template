import logging

BOT_TOKEN = ''
BASE_URL = 'https://example.com'  # Webhook domain
WEBHOOK_PATH = f'/tg/webhooks/bot/{BOT_TOKEN}'
WEBHOOK_URL = f'{BASE_URL}{WEBHOOK_PATH}'

LOGGING_LEVEL = logging.WARNING

ADMINS = []

POSTGRES_CREDS = {
    'host':     '',
    'user':     '',
    'password': '',
    'database': '',
    'port':     5432,
}

REDIS_CREDS = {
    'host':     '',
    'password': ''
}
