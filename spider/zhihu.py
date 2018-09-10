from util.function import (
    url_with_querys,
    assign_values,
    load_json,
)
from db.queue import Queue, Key
from manager.proxy_manager import ProxyManager
from util.web_request import WebRequest

import config
import secret
import time

class ZhihuUserSpider(object):
    '''
    zhihu user spider
    
    通过 zhihu api 爬取数据
    '''
    _base_url = 'https://www.zhihu.com/api/v4/members'
    gender_mapping = {
        -1: 'unknown',
        0: 'female',
        1: 'male',
    }
    fields = [
        'locations',  # 位置
        'employments',  # 就职经历
        'gender',  # 性别 -1: 未知, 0: 女, 1: 男
        'educations',  # 教育经历
        'business',  # 行业
        'voteup_count',  # 赞同数目
        'thanked_count',  # 感谢数目
        'follower_count',  # 关注者数目
        'following_count',  # 所关注的数目
        'answer_count',  # 回答数目
        'articles_count',  # 文章数目
        'pins_count',  # 想法数目
        'question_count',  # 问题数目
        'favorited_count',  # 被收藏的数目
        'industry_category'
    ]

    pm = ProxyManager()
    requests = WebRequest()

    @classmethod
    def request_json(cls, url):
        p = cls.pm.get()

        headers = {
            'Cookie': secret.cookie,
        }
        # 在成功请求到数据 / 或已经没有可使用的代理 之前一直循环
        while True:
            host, port = p
            u = 'http://{}:{}'.format(host, port)
            # print('>>> {:30s}'.format(u), end=' ')
            ps = {
                'http': u,
                'https': u,
            }
            try:
                r = cls.requests.get(
                    url, headers=headers, proxies=ps,
                    timeout=config.TIMEOUT
                )
                if r is None:
                    cls.pm.delete(p)
                    raise Exception
            except Exception:
                # print('failed. {} proxies left.'.format(len(all_proxies)))
                p = cls.pm.get()
                continue
            text = r.text
            data = load_json(text)
            if data is None:
                # print('failed. {} proxies left.'.format(len(all_proxies)))
                p = cls.pm.get()
            else:
                return data

    @classmethod
    def retrieve_user_data(cls, data):
        '''
        从单个用户的数据中提取出所需信息

        data:
            爬取到的数据字典，keys 与 cls.fields 对应
        '''
        u = {}
        assign_values(data, u, [
            {'from': 'url_token', 'to': 'id'},
            {'from': 'name'},
            {'from': 'gender', 'handler': lambda g: cls.gender_mapping[g]},
            {'from': 'locations', 'handler': lambda l: l[0]['name'] if len(l) > 0 else ''},
            {'from': 'educations', 'handler': lambda e: ','.join(
                item['school']['name'] for item in e if 'school' in item
            )},
            {'from': 'employments', 'to': 'careers', 'handler': lambda e: ','.join(
                [i['company']['name'] for i in e if 'company' in i]
            )},
            {'from': 'business', 'to': 'profession', 'handler': lambda b: b['name']},
            {'from': 'pins_count'},
            {'from': 'answer_count'},
            {'from': 'articles_count'},
            {'from': 'question_count'},
            {'from': 'follower_count'},
            {'from': 'following_count', 'to': 'followee_count'},
            {'from': 'favorited_count'},
            {'from': 'thanked_count'},
            {'from': 'voteup_count', 'to': 'thumbup_count'},
        ])
        return u

    @classmethod
    def get_followees(cls, user_token, page=1, num_per_page=20):
        '''
        得到 user_token 对应用户的关注者

        user_token:
            用户用于注册的唯一 token
        page:
            zhihu api 将用户关注者按页分开，page 表示是第几页
        num_per_page:
            每页有多少个用户
        '''
        # 计算关注者区间的起点
        offset = num_per_page * (page - 1)
        url = url_with_querys('{}/{}/followees'.format(cls._base_url, user_token), {
            'include': 'data[*].{}'.format(','.join(cls.fields)),
            'offset': offset,
            'limit': num_per_page,
        })
        dataset = cls.request_json(url)
        data = dataset.get('data')
        if data:
            for d in data:
                yield cls.retrieve_user_data(d)

    @classmethod
    def get_user(cls, user_token):
        url = url_with_querys('{}/{}'.format(cls._base_url, user_token), {
            'include': ','.join(cls.fields),
        })
        # print(u)
        data = cls.request_json(url)

        return cls.retrieve_user_data(data)


def prepare_crawl(existed_users):
    print('>>> preparing user data to crawl...')
    if existed_users is None or len(existed_users) == 0:
        user_tokens = ['roly-62']
        for t in user_tokens:
            user = ZhihuUserSpider.get_user(t)
            # 保存用户
            Queue.enqueue(Key.CRAWLED_USERS.name, user)
            # 放到队列中，等待进一步爬取
            Queue.enqueue(Key.USERS_TO_CRAWL.name, [user['id'], user['followee_count']])
            print('>>> [prepare_crawl] get {}'.format(user['id']))
    else:
        for u in existed_users:
            # 用户已存在，接下来需要放到队列中，检查进一步的爬取
            Queue.enqueue(Key.USERS_TO_CRAWL.name, [u.id, u.followee_count])
            print('>>> [prepare_crawl] get {}'.format(u.id))
    print('>>> prepare done.')

def crawl():
    # 从队列中取得需要爬取的用户，爬取用户的关注者列表中的用户
    data = Queue.dequeue(Key.USERS_TO_CRAWL.name)
    token, followee_count = data
    page = 0
    num_per_page = 20
    while followee_count > 0:
        page += 1
        followee_count -= num_per_page
            
        for user in ZhihuUserSpider.get_followees(
            token,
            page=page,
            num_per_page=num_per_page
        ):
            # 爬取到的数据保存到队列中
            Queue.enqueue(Key.CRAWLED_USERS.name, user)

        time.sleep(config.CRAWL_WAIT_TIME)


from gevent import monkey; monkey.patch_socket()
import gevent

def concurrent_crawl():
    spawns = [gevent.spawn(crawl) for _ in range(
        config.MAX_CRAWL_CONCURRENT_PER_PROCESS
    )]
    gevent.joinall(spawns)


from bloom_filter import BloomFilter

bloom_filter = BloomFilter()


def init_filter(tokens=[]):
    for t in tokens:
        bloom_filter.add(t)


def user_filter(existed_tokens):
    check_nums = 0
    # 把已经存在的用户 token 放到 filter 中
    init_filter(existed_tokens)
    while True:
        # 从队列中取出爬取到的用户数据
        user = Queue.dequeue(Key.CRAWLED_USERS.name)
        if type(user) == str:
            with open('err.txt', 'a+') as f:
                print(user, file=f)
        
        check_nums += 1
        token = user['id']
        # 只有 token 不存在时（即没有被爬过的用户），才进行保存以及进一步的爬取
        if token not in bloom_filter:
            bloom_filter.add(token)
            # 放到 USERS_TO_SAVE 队列中，等待保存
            Queue.enqueue(Key.USERS_TO_SAVE.name, user)
            # 放到 USERS_TO_CRAWL 队列中，等待进一步爬取
            Queue.enqueue(Key.USERS_TO_CRAWL.name, [token, user['followee_count']])
        print('>>> check users num: {}'.format(check_nums))


from models.user import User

def store_data():
    '''
    从队列中读取装有用户数据的字典，保存到数据库中
    '''
    success_num = 0
    fail_num = 0
    while True:
        try:
            # 从 USERS_TO_SAVE 队列中取出需要保存的用户数据
            data = Queue.dequeue(Key.USERS_TO_SAVE.name)
            # 通过 User 类保存
            User(**data).save()
            success_num += 1
        except BaseException as e:
            print(e)
            fail_num += 1

        print('user----->>>>>>>>Successed num: {}, Failed num: {}\r'.format(success_num, fail_num))


if __name__ == '__main__':
    from multiprocessing import Process

    ps = [
        Process(target=prepare_crawl),
        Process(target=concurrent_crawl),
        Process(target=user_filter),
        Process(target=store_data),
    ]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
