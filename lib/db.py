import aiofiles
import aiosqlite
from conf.config import DB_PATH, TABLE_NAME


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
        db = await aiosqlite.connect(DB_PATH)
        cursor = await db.execute(f"SELECT count FROM {TABLE_NAME} where path='{current_path}'")
        old_count = await cursor.fetchone()
        try:
            new_count = old_count[0] + 1
            update_count_sql = '''update {} set count={} where path="{}"'''.format(TABLE_NAME, new_count, current_path)
            print(f'当前更新sql为: {update_count_sql}')
            await db.execute(update_count_sql)
        except Exception:
            pass
        await db.commit()
        await cursor.close()
        await db.close()
