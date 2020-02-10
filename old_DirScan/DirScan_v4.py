import csv
import time
import random
import asyncio
import httpx
import aiofiles
import aiosqlite
import sys
from bs4 import BeautifulSoup
from httpx.exceptions import HTTPError
from optparse import OptionParser
from urllib.parse import urlparse


async def judge_path_status(client, q):
    while not q.empty():
        url_path = q.get_nowait()
        response = await get_req(client, url_path)
        if response:
            status_code, title = response.status_code, parse_title(
                response)
            output_item = ''
            if response.headers.get('Content-Length', None):
                content_length = response.headers.get("Content-Length")
                output_item = f'{url_path} | {str(response.status_code)} | {title} | {content_length}'
            else:
                content_length = len(response.text)
                output_item = f'{url_path} | {str(response.status_code)} | {title} | {content_length}'
            if status_code == 404:
                print(f'{url_path} 应该不存在')
            elif status_code == 200:
                if "404.css" in response.text or "404.js" in response.text or "404.html" in response.text or "404" in response.text or "not found" in response.text:  # 如果页面有404相关信息则目录可能不存在
                    print(f'{url_path} ==> 当前页面是响应码200的404页面!!!')
                else:
                    # 对比随机url进行判断
                    random_url = get_random_url(output_item)
                    random_url_response = await get_req(client, random_url)
                    if random_url_response:
                        random_status_code = random_url_response.status_code
                        # 判断随机url的响应码
                        if random_status_code == 200:
                            content_length = response.headers.get('Content-Length', None)
                            random_content_length = random_url_response.headers.get('Content-Length', None)
                            if content_length or random_content_length:
                                if content_length == random_content_length:
                                    print(f'{url_path} 可能不存在')
                                else:
                                    print(f'{url_path} 可能存在')
                                    await save_result('可能存在的路径.txt', output_item, urlparse(url_path)[2])
                            else:
                                random_content_length = len(random_url_response.text)
                                root_content_length = len(response.text)
                                if root_content_length == random_content_length:  # 相等则小概率网站正常
                                    print(f"{url_path}  可能存在")
                                else:  # conteng-length不想等说明网站有大概率正常，访问正常网站和随机url正常来说content-length就应该不一样
                                    print(f"{url_path} 可能正常")
                                    await save_result('01 - 应该存在的路径.txt', output_item, urlparse(url_path)[2])
                        elif random_status_code == 404:
                            print(f'{url_path} 应该存在')
                            await save_result('01 - 应该存在的路径.txt', output_item, urlparse(url_path)[2])
            elif status_code == 403:
                random_url = get_random_url(url_path)
                random_url_response = await get_req(client, random_url)
                if random_url_response:
                    random_status_code = random_url_response.status_code
                    if random_status_code == 404:
                        print(f'{url_path} 应该ok')
                        await save_result('01 - 应该存在的路径.txt', output_item, urlparse(url_path)[2])
                    else:
                        print(f'{url_path} 应该不存在')
            elif '30' in str(status_code):
                print(f'{url_path} 可能存在或者跳转404')
            elif status_code in [401, 415]:
                print(f'{url_path} 应该存在')
                await save_result('', output_item, urlparse(url_path)[2])
            else:
                pass
        else:
            print(url_path, ' => 响应为None')


def get_random_url(url_path):
    random_string = "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', 9))
    random_url = url_path + random_string
    return random_url


async def get_req(client, url, redirect=False):
    '''
    异步请求协程
    :param client:
    :param url:
    :param redirect:
    :return:
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    try:
        response = await client.get(url, allow_redirects=redirect, headers=headers, timeout=15)
        if "30" in str(response.status_code):
            try:
                r = await get_req(client, url, redirect=True)
                if r:
                    if r.status_code in [200, 401, 403, 404, 415]:
                        return r
                    else:
                        return None
                else:
                    return None
            except HTTPError as e:
                output_item = f'{url} | {e}'
                await save_result('DirScan - 异常处理.txt', output_item)
                return None
        return response
    except HTTPError as e:
        output_item = f'{url} | {e}'
        await save_result('DirScan - 异常处理.txt', output_item)
        return None


def parse_title(response):
    '''
    解析 html title 或者 json文本
    :param response:
    :return:
    '''
    if response.text:
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        # print('soup', soup)
        if soup.title:
            title = soup.title.string
            return title
        elif response.headers.get('Content-Type', None):
            if 'json' in response.headers.get('Content-Type', None):
                return response.json()
            else:
                return None
        else:
            return None
    else:
        return None


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
        print(f'{url_path} ==> 加入queue')
    print(f'qsize: {q.qsize()}')


def gen_one_csv(csv_filename, url_status_set):
    test_list = []
    for site_status_info in url_status_set:
        site_status_info = site_status_info.split('|')
        test_list.append(site_status_info)

    headers = ['Url', 'Status Code', 'Title', 'Content_Length']
    with open('{}.csv'.format(csv_filename), 'w', newline='', encoding='utf-8')as f:
        f_csv = csv.writer(f, delimiter='|')
        f_csv.writerow(headers)
        f_csv.writerows(test_list)


async def save_result(output_file, output_item, current_path=None):
    '''
    1、保存txt类型
    2、更新sqlite中count字段
    :param output_file:
    :param output_item:
    :param current_path:
    :return:
    '''
    async with aiofiles.open(output_file, mode='a+') as f:
        await f.write(f'{output_item}\n')
    if current_path:
        db = await aiosqlite.connect(sqlite_db_path)
        cursor = await db.execute(f"SELECT count FROM {table_name} where path='{current_path}'")
        old_count = await cursor.fetchone()
        new_count = old_count[0] + 1
        update_count_sql = '''update {} set count={} where path="{}"'''.format(table_name, new_count, current_path)
        print(f'当前更新sql为: {update_count_sql}')
        await db.execute(update_count_sql)
        await db.commit()
        await cursor.close()
        await db.close()


async def main():
    '''
    main函数
    :return:
    '''
    async with httpx.AsyncClient(verify=False) as client:  # 创建session
        tasks = []
        for _ in range(300):
            task = judge_path_status(client, q)
            tasks.append(task)
        await asyncio.wait(tasks)


# todo code 200 too many handle
code_200_dict = {}

if __name__ == '__main__':
    start_time = time.time()
    parser = OptionParser()
    parser.add_option(
        "-u",
        "--urls",
        dest='urls_file',
        help='target urls file')
    parser.add_option("-d", "--dict", dest='dict_file', help='dict file')
    parser.add_option(
        "-t",
        "--thread",
        dest='threads_num',
        type=int,
        help='thread nums')
    (options, args) = parser.parse_args()

    if options.urls_file and options.dict_file and options.threads_num:
        sqlite_db_path = 'all_type_dict.db'
        table_name = 'jsp_path'
        queue_put(options.urls_file, options.dict_file)
        asyncio.run(main())
        print(f'Cost time: {time.time() - start_time}')
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
