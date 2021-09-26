import os
from pathlib import Path

PORT = 8877
BOT_TOKEN = os.environ["bot_token"]
WEBHOOK_PATH = f'/tg/webhooks/bot/{BOT_TOKEN}'

LOGS_BASE_PATH = str(Path(__file__).parent.parent / 'logs')

admins = []

mongo = {
    'hostname':  '127.0.0.1',
    'password': 'root',
    'username':  'example',
    'port': 27017,
    'database': 'telegram_bot'
}
