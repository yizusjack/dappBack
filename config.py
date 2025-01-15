from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    pass

class DbConfig(Config):
    DEBUG = os.getenv('DEBUG')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle' : 280}

config = {
    'development': DbConfig,
}