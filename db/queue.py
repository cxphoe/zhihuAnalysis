import redis
import json
from enum import Enum, auto


class Queue(object):
    r = redis.StrictRedis(host='localhost', port=6379)

    @classmethod
    def enqueue(cls, key, value):
        cls.r.rpush(key, value)
    
    @classmethod
    def dequeue(cls, key):
        _, value = cls.r.brpop(key)
        value = value.decode().replace('\'', '"')
        try:
            return json.loads(value)
        except Exception:
            return value


class Key(Enum):
    CRAWLED_USERS = auto()
    USERS_TO_CRAWL = auto()
    USERS_TO_SAVE = auto()

    def translate(self, _escape_table):
        return self.name