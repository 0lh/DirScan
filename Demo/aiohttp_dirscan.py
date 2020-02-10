import asyncio
import aiohttp
from lxml import html
from queue import Queue

headers = {
    "User-Agent": "Mozilla/5.0 (Windo  ws NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}


async def get_req(url):
    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:  # 创建session
        async with session.get(url, headers=headers, allow_redirects=False, timeout=4) as req:
            if req.status == 200:  # 判断请求码
                source = await req.text()  # 使用await关键字获取返回结果
                try:
                    print(f'{url} ==> 状态码 {req.status} ' + html.fromstring(source).xpath("//title/text()")[
                        0].strip())  # 获取网页标题
                    print("=" * 30)
                except Exception as e:
                    # print(f'{url} => ERROR')
                    pass
            else:
                # print(f'{url} => 访问失败')
                pass


q = Queue(-1)


def queue_put_urls():
    with open('../urls.txt', 'r') as f:
        for url in f:
            q.put(url.strip('\n'))
    print(f'queue urls 数量 {q.qsize()}')


if __name__ == '__main__':
    # queue_put_urls()
    event_loop = asyncio.get_event_loop()
    tasks = []
    with open('../urls.txt', 'r') as urls:
        for url in urls:
            with open('../dir_dict.txt', 'r') as dir_dict:
                for dir in dir_dict:
                    url_dir = url.strip('\n') + dir.strip('\n')
                    future = get_req(url_dir)
                    tasks.append(future)

    results = event_loop.run_until_complete(asyncio.wait(tasks))
