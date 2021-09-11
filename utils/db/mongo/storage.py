import motor.motor_asyncio as m_m_a
from data import config


class BaseMongo:
    client = None
    db = None

    @staticmethod
    def get_client():
        if BaseMongo.client is None:
            BaseMongo.client = m_m_a.AsyncIOMotorClient("mongodb://{}:{}@{}:{}".format(
                 config.mongo['password'], config.mongo['username'], config.mongo['hostname'], str(config.mongo['port'])))

        return BaseMongo.client

    @staticmethod
    def get_data_base():
        if BaseMongo.db is None:
            client = BaseMongo.get_client()
            BaseMongo.db = client[config.mongo['database']]

        return BaseMongo.db