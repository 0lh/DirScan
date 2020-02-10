import sys
import time
import csv
import requests
from pyquery import PyQuery as pq
from requests import exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from optparse import OptionParser
from concurrent.futures import ThreadPoolExecutor, as_completed


def req_parse(url):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
    }
    try:
        # 重试机制
        s = requests.Session()
        retries = Retry(total=5, status_forcelist=[500, 501, 502, 503, 504])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        s.mount('https://', HTTPAdapter(max_retries=retries))
        requests.packages.urllib3.disable_warnings()
        response = s.get(url, headers=headers, allow_redirects=False, verify=False, timeout=4)
    except exceptions.Timeout as e:
        pass
    except exceptions.HTTPError as e:
        # print('[ERROR!!!] ', e)
        pass
    except Exception as e:
        # print("[ERROR] {} ===> 通用异常处理!!!\n".format(url))
        pass
    else:
        if 'html' in response.headers['Content-Type']:
            try:
                html = pq(response.text)
            except Exception as e:
                pass
            else:
                title = html('title').text().strip()
                # print(f'[+] url: {url} => {response.status_code} => {title}')
                return url, response.status_code, title

        elif response.headers['Content-Type'] == 'application/json':
            # print(f'[JSON] url: {url} => {response.status_code} => json信息 => {response.text}')
            return url, response.status_code, response.text


all_task = []


def scan_thread(urls_file, dict_file, threads_num):
    # 启动20个线程
    with ThreadPoolExecutor(threads_num) as executor:
        with open(urls_file, 'r') as urls:
            for root_url in urls:
                with open(dict_file, 'r') as dir_dict:
                    for dir in dir_dict:
                        url_dir = root_url.strip('\n') + '/' + dir.strip('\n')
                        print(f'正在访问 {url_dir}')
                        all_task.append(executor.submit(req_parse, (url_dir)))


def save_csv():
    pass


if __name__ == '__main__':
    start_time = time.time()
    parser = OptionParser()
    parser.add_option("-u", "--urls", dest='urls_file', help='target urls file')
    parser.add_option("-d", "--dict", dest='dict_file', help='dict file')
    parser.add_option("-t", "--thread", dest='threads_num', type=int, help='thread nums')
    (options, args) = parser.parse_args()

    if options.urls_file and options.dict_file and options.threads_num:
        scan_thread(options.urls_file, options.dict_file, options.threads_num)
        print(len(all_task))
        print('=' * 30)

        # 打印结果集
        with open('output.txt', 'a+') as f:
            for future in as_completed(all_task):
                data = future.result()
                if data != None:
                    f.write(f'{data[0]} | {data[1]} | {data[2]}\n')
            # print(f'[+] {data}')
        end_time = time.time()
        print(f'Cost time: {end_time - start_time}')
        sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)
