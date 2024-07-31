import os
basedir = os.path.abspath(os.path.dirname(__name__))

class Config():
    DEBUG = False
    SQLITEDB_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITEDB_DB_DIR = os.path.join(basedir,'database')
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(SQLITEDB_DB_DIR,"database.sqlite3")
    DEBUG = True
