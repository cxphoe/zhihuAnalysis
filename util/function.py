import json, os, requests
from pyquery import PyQuery as pq

_base_path = 'data'

def save(data, filename):
    if not os.path.exists(_base_path):
        os.makedirs(_base_path)

    data = json.dumps(data, ensure_ascii=False)
    with open('{}/{}.txt'.format(_base_path, filename), 'w', encoding='utf8') as f:
        f.write(data)


def retrieve_int(str):
    '''
    提取数字
    str: 一个带有逗号分隔符的数字字符串
    '''
    return ''.join(part.strip() for part in str.split(','))


def url_with_querys(url, querys):
    return '{}?{}'.format(
        url,
        '&'.join('{}={}'.format(k, v) for k, v in querys.items()),
    )


def assign_values(source, obj, translates):
    '''
    把来源的数据赋值给字典，通过给定的配置进行对来源的数据 直接/处理完之后 传给目标字典
    
    source:
        数据来源, dict
    obj:
        赋值字典, dict
    translate:
        赋值的配置数组，包括多个配置字典: 有 from, to, handler 三个配置项
        根据每个配置会有 setattr(obj, to, source[from] / handler(source[from]))
        from: 在 source 中的键，必需
        to: 在 obj 中的键，可以不设置，默认与 from 相同
        handler: 用于处理 source[from] 数据，可以不设置
    '''
    for t in translates:
        # from 是必需的
        fr = t['from']
        if fr not in source:
            # 属性不存在，跳过
            continue

        # 没有传入 from 时，默认 to 与 from 相同
        to = t.get('to', fr)
        handler = t.get('handler') 
        value = source[fr]
        if callable(handler):
            value = handler(value)
        obj[to] = value


def load_json(text):
    try:
        data = json.loads(text, encoding='utf8', strict=False)
        if not data:
            raise Exception
        return data
    except Exception:
        # print('load json failed.')
        print('\n\n{}\n'.format(text[:1000]))

