from requests.models import Response
import requests
import random
import time


class WebRequest(object):

    def __init__(self):
        pass

    @property
    def user_agent(self):
        '''
        返回一个随机的 user-agent
        '''
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def headers(self):
        return {
            'User-Agent': self.user_agent,
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        }

    def get(self, url, headers=None, retry_times=5,
            timeout=10, retry_interval=3, *args, **kwargs):
        '''
        method get
        '''
        _headers = self.headers
        if headers and isinstance(headers, dict):
            _headers.update(headers)
        while True:
            try:
                # 尝试发出请求
                r = requests.get(url, headers=_headers,
                                 timeout=timeout, **kwargs)
                return r
            except Exception as e:
                print('>>> {:30s} failed'.format(kwargs['proxies']['http'].split('//')[1]))
                # 失败则判断尝试次数，> 0 继续尝试；否则，返回 None
                retry_times -= 1
                if retry_times <= 0:
                    return None
                else:
                    time.sleep(retry_interval)


if __name__ == '__main__':
    web_request = WebRequest()
    r = web_request.get('https://www.zhihu.com/')
    print(r.ok, r)
