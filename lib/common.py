import random
import time


def get_random_url(root_url: str) -> str:
    '''
    生成随机url
    '''
    random_string = '/' + \
                    "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 9))
    random_url = root_url + random_string
    return random_url


def cost_time(func):
    def _log(*args, **kwargs):
        beg = time.time()
        res = func(*args, **kwargs)
        print(f'Use time: {time.time() - beg}')
        return res

    return _log
