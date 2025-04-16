import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback'
    MONGO_URI = os.environ.get('MONGO_URI')