from pymongo import MongoClient
from flask import current_app
import ssl

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
        return cls._instance

    def get_client(self):
        if self.client is None:
            mongo_uri = current_app.config['MONGO_URI']
            ssl_verify = current_app.config.get('MONGO_SSL_VERIFY', True)

            ssl_cert_reqs = ssl.CERT_REQUIRED if ssl_verify else ssl.CERT_NONE

            self.client = MongoClient(mongo_uri, ssl=True, ssl_cert_reqs=ssl_cert_reqs)
        return self.client

def get_db():
    return Database()