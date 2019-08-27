import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_ECHO = False
    SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = "sqlite:///flight_deals.db"

class ProductionConfig(Config):
    DEBUG = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
