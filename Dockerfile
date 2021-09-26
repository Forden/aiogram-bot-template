FROM python:3.7-slim

WORKDIR /botname

ENV bot_token="do not post your token here"
COPY requirements.txt /botname/
RUN pip install -r /botname/requirements.txt
COPY . /botname/
CMD python3 /botname/bot.py
