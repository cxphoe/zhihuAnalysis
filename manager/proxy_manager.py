import random
from util.function import (
    load_json,
)
import json

def get_proxies():
    with open('proxies.json') as f:
        return load_json(f.read())

class ProxyManager(object):
    proxies = get_proxies()

    @classmethod
    def get(cls):
        if len(cls.proxies) > 0:
            return random.choice(cls.proxies)
        else:
            return None
    
    @classmethod
    def delete(cls, proxy):
        print('delete', proxy)
        h, po = proxy
        for i in range(len(cls.proxies)):
            host, port = cls.proxies[i]
            if host == h and port == po:
                print(i)
                cls.proxies.pop(i)
                with open('proxies.json', 'w') as f:
                    f.write(json.dumps(cls.proxies))
                break
