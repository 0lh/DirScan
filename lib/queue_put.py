import asyncio
from itertools import product
import aiofiles
from urllib.parse import urlparse


# todo 拆分queue put url_path 成单独模块

def get_urls(urls_file):
    '''
    添加到urls_list
    '''
    urls_list = []
    with open(urls_file, 'r', encoding='utf-8') as urls:
        for url in urls:
            # yield url.rstrip('\n').rstrip()
            urls_list.append(url.rstrip('\n').rstrip())
    return urls_list


# 拼接第一层
def get_url_path(urls_list, dir_dict=None, filenames_dict=None):
    '''
    获取目录字典文件，遍历urls生成器，拼接url_path
    '''
    if dir_dict:
        with open(dir_dict, 'r', encoding='utf-8') as paths:
            for url in urls_list:
                for path in paths:
                    yield url + path.rstrip('\n')

    if filenames_dict:
        with open(filenames_dict, 'r', encoding='utf-8') as paths:
            for url in urls_list:
                for path in paths:
                    yield url + path.rstrip('\n')


q = asyncio.Queue()


def queue_put(urls_file, dir_dict=None, filenames_dict=None):
    urls_list = get_urls(urls_file)
    paths = get_url_path(urls_list, dir_dict, filenames_dict)
    for url_path in paths:
        print(url_path, ' -> 正在导入asyncio.queue')
        q.put_nowait(url_path)
    print(f'qsize: {q.qsize()}')


suffix_list = ['.php', '.js', '.jsp', '.html', '.apsx', '.asp', '.zip', '.www', '.d']


async def queue_put_url(url, dir_dict=None, filenames_dict=None):
    if '.' not in urlparse(url)[2].split('/')[-1]:  # 是目录或者无后缀文件名，直接拼接
        print(f'{url} 结尾无 ".",应该是目录，继续拼接路径扫描')
        if dir_dict:
            async with aiofiles.open(dir_dict) as paths:
                async for path in paths:
                    print('异步put to queue：', url + path.rstrip('\n'))
                    q.put_nowait(url + path.rstrip('\n'))
        if filenames_dict:
            async with aiofiles.open(filenames_dict) as paths:
                async for path in paths:
                    print('异步put to queue：', url + path.rstrip('\n'))
                    q.put_nowait(url + path.rstrip('\n'))
    else:
        print(f'{url} 结尾有 ".",不继续拼接路径扫描')


if __name__ == '__main__':
    urls_file = 'D:\\Tools\\自动化脚本\\DirScan\\data\\small.txt'
    dir_dict = 'D:\\Tools\\自动化脚本\\DirScan\\data\\dir_dict.txt'
    filename_dict = 'D:\\Tools\\自动化脚本\\DirScan\\data\\filename_dict.txt'
    queue_put_url('http://192.168.3.2')
