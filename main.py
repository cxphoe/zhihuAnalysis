import psutil
import sys

from multiprocessing import Process
from spider.zhihu import(
    prepare_crawl,
    concurrent_crawl,
    user_filter,
    store_data,
)
from db import SQLDB
from models.user import User


def get_user_tokens():
    '''
    得到已经存在的 user_token，作为爬虫的源头
    '''
    return list(User.all())


def reset_database():
    '''
    清楚数据库中的用户数据
    '''
    SQLDB.drop_db()
    SQLDB.init_db()


def main(argv):
    if '--reset' in argv:
        reset_database()
        users = []
    else:
        users = get_user_tokens()
        print('>>> {} users found'.format(len(users)))
    tokens = [u.id for u in users]

    ps = [
        Process(target=prepare_crawl, args=(users,)),
        Process(target=user_filter, args=(tokens,)),
        Process(target=store_data),
    ]
    concurrent_count = psutil.cpu_count() - 2
    if concurrent_count <= 0:
        concurrent_count = 1
    for _ in range(concurrent_count):
        p = Process(target=concurrent_crawl)
        ps.append(p)

    for p in ps:
        p.start()
    for p in ps:
        p.join()


if __name__ == '__main__':
    main(sys.argv[1:])

