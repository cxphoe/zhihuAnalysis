from sqlalchemy import create_engine
from db import SQLDB
import secret

def reset_database():
    db = secret.db_name

    engine = create_engine(
        "mysql+pymysql://root:{}@localhost/?charset=utf8mb4".format(secret.db_password)
    )

    with engine.connect() as c:
        c.execute(
            'DROP DATABASE IF EXISTS {}'.format(db)
        )
        c.execute(
            # 加上 charset utf8 collate utf8_general_ci，否则插入中文会出错
            'CREATE DATABASE {} charset utf8 collate utf8_general_ci'.format(db)
        )
        c.execute(
            'USE {}'.format(db)
        )

    SQLDB.init_db()

def main():
    reset_database()

if __name__ == '__main__':
    main()