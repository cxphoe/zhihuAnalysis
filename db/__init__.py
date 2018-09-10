from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

import secret

Base = declarative_base()
engine = create_engine(
    "mysql+pymysql://root:{}@localhost/{}?charset=utf8mb4".format(secret.db_password, secret.db_name)
)


class SQLDB(object):
    engine = engine
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    @classmethod
    def init_db(cls):
        Base.metadata.create_all(cls.engine)

    @classmethod
    def drop_db(cls):
        Base.metadata.drop_all(cls.engine)

