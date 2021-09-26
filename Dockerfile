FROM python:3.7-slim

WORKDIR /botname

ARG token_setter
ENV bot_token=$token_setter
COPY requirements.txt /botname/
RUN pip install -r /botname/requirements.txt
COPY . /botname/
CMD python3 /botname/bot.py
