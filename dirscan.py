import asyncio
import httpx
import time
from core.core import judge_path_status
from lib.queue_put import q, queue_put, queue_put_url
from lib.cmdline import parse_args
from conf.config import COROS_NUM


async def main():
    '''
    main函数
    :return:
    '''
    async with httpx.AsyncClient(verify=False) as client:  # 创建session
        tasks = []
        for _ in range(COROS_NUM):
            task = judge_path_status(client, q)
            tasks.append(task)
        await asyncio.wait(tasks)


if __name__ == '__main__':
    start_time = time.time()
    argv = parse_args()
    urls_file, dict_file = argv.target, argv.path
    queue_put(urls_file, dict_file)
    asyncio.run(main())
    print(f'Cost time: {time.time() - start_time}')
