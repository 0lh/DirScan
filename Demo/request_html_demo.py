from requests_html import HTMLSession

session = HTMLSession()
r = session.get('https://www.baidu.com', allow_redirects=False, verify=False, timeout=4)


class DirScan():
    def __init__(self, url):
        self.session = HTMLSession()
        # 循环取出url
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        self.timeout = 4

    def get_title(self):
        try:
            response = session.get(self.url, allow_redirects=False, verify=False, timeout=4)
        except:
            print('出错了')
        else:
            if response.status_code == 200:
                response.encoding = response.apparent_encoding
                title_name = self.parse_title(response)
                print('title name ', title_name)
                return title_name

    def parse_title(self, response):
        title_name = response.html.find('title', first=True)
        return title_name


all_task = []
from concurrent.futures import ThreadPoolExecutor, as_completed


def scan_thread(urls_file, dict_file, threads_num):
    # 启动20个线程
    with ThreadPoolExecutor(threads_num) as executor:
        with open(urls_file, 'r') as urls:
            for root_url in urls:
                with open(dict_file, 'r') as dir_dict:
                    for dir in dir_dict:
                        url_dir = root_url.strip('\n') + '/' + dir.strip('\n')
                        print(f'正在访问 {url_dir}')
                        task = DirScan(url_dir).get_title()
                        all_task.append(executor.submit(task, ()))


if __name__ == '__main__':
    scan_thread('../urls.txt', 'dir_dict.txt', 20)
