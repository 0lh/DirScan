import asyncio
import click
from conf.config import URLS_FILE


# todo 拆分queue put url_path 成单独模块
def get_urls(urls_file):
    '''
    生成器函数，yield url
    '''
    with open(urls_file, 'r', encoding='utf-8') as urls:
        for url in urls:
            yield url.rstrip('\n').rstrip()


def get_url_path(urls, paths_file):
    '''
    获取目录字典文件，遍历urls生成器，拼接url_path
    '''
    for url in urls:
        with open(paths_file, 'r', encoding='utf-8') as paths:
            for path in paths:
                yield url + path.rstrip('\n')


q = asyncio.Queue()


# todo 有价值的url列表，


def queue_put(urls_file, paths_file):
    '''
    遍历all_url_path生成器中的 url_path put到queue中
    '''
    urls = get_urls(urls_file)
    all_url_path = get_url_path(urls, paths_file)
    for url_path in all_url_path:
        q.put_nowait(url_path)
        # print(f'{url_path} ==> 加入queue')
    print(f'qsize: {q.qsize()}')


async def queue_put_url(url, dict_dir=None, dict_filename=None):
    with open(dict_dir, 'r', encoding='utf-8') as dirs:
        for path in dirs:
            yield url + path.rstrip('\n')

    with open(dict_filename, 'r', encoding='utf-8') as files:
        for path in files:
            yield url + path.rstrip('\n')
