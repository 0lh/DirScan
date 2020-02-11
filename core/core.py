from lib.request import get_req
from urllib.parse import urlparse
from lib.parse import parse_title
from collections import Counter
from lib.common import get_random_url
from lib.db import save_result
from conf.config import SAVE_FILE_01, SAVE_FILE_02, SAVE_FILE_03, SAVE_FILE_04, SAVE_FILE_05
from lib.queue_put import queue_put_url
from lib.cmdline import parse_args

bad_url_set = set()
code_200_list = []
# dir_dict = 'D:\\Tools\\自动化脚本\\DirScan\\data\\dir_dict.txt'
# filename_dict = 'D:\\Tools\\自动化脚本\\DirScan\\data\\filename_dict.txt'

argv = parse_args()
dir_dict, filename_dict = argv.dirs, argv.filenames


async def judge_path_status(client, q):
    while not q.empty():
        url_path = q.get_nowait()
        current_root_url = f'{urlparse(url_path)[0]}://{urlparse(url_path)[1]}'
        if current_root_url not in bad_url_set:
            response = await get_req(client, url_path)
            if response:
                status_code, title = response.status_code, parse_title(response)
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
                    code_200_list.append(current_root_url)
                    if Counter(code_200_list)[current_root_url] <= 50:
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
                                            await save_result(SAVE_FILE_02, output_item, urlparse(url_path)[2])
                                            await queue_put_url(url_path, dir_dict, filename_dict)
                                    else:
                                        random_content_length = len(random_url_response.text)
                                        root_content_length = len(response.text)
                                        if root_content_length == random_content_length:  # 相等则小概率网站正常
                                            print(f"{url_path}  可能存在")
                                        else:  # conteng-length不想等说明网站有大概率正常，访问正常网站和随机url正常来说content-length就应该不一样
                                            print(f"{url_path} 可能正常")
                                            await save_result(SAVE_FILE_01, output_item, urlparse(url_path)[2])
                                            await queue_put_url(url_path, dir_dict, filename_dict)
                                elif random_status_code == 404:
                                    print(f'{url_path} 应该存在')
                                    await save_result(SAVE_FILE_01, output_item, urlparse(url_path)[2])
                                    await queue_put_url(url_path, dir_dict, filename_dict)
                    else:  # 添加bad_url_set
                        bad_url_set.add(current_root_url)
                elif status_code == 403:
                    random_url = get_random_url(url_path)
                    random_url_response = await get_req(client, random_url)
                    if random_url_response:
                        random_status_code = random_url_response.status_code
                        if random_status_code == 404:
                            print(f'{url_path} 应该ok')
                            await save_result(SAVE_FILE_01, output_item, urlparse(url_path)[2])
                            await queue_put_url(url_path, dir_dict, filename_dict)
                        else:
                            print(f'{url_path} 应该不存在')
                elif '30' in str(status_code):
                    print(f'{url_path} 可能存在或者跳转404')
                    await save_result(SAVE_FILE_02, output_item, urlparse(url_path)[2])
                    await queue_put_url(url_path, dir_dict, filename_dict)
                elif status_code in [401, 415]:
                    print(f'{url_path} 应该存在')
                    await save_result(SAVE_FILE_01, output_item, urlparse(url_path)[2])
                    await queue_put_url(url_path, dir_dict, filename_dict)
                else:
                    await save_result(SAVE_FILE_05, output_item, urlparse(url_path)[2])
                    await queue_put_url(url_path, dir_dict, filename_dict)
            else:
                print(url_path, ' => 响应为None')
        else:
            print(f'{current_root_url} ==> bad url')
