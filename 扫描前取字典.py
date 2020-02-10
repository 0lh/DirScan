import sqlite3
import datetime

sqlite_db_path = 'D:\\Tools\\自动化脚本\\CMS字典分类收集\\all_type_dict.db'


def select_path_from(table_name, row_num):
    today = datetime.date.today()
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()
    query_sql = '''select path,count from {} order by count desc limit {};'''.format(table_name, row_num)
    print('当前查询语句 => ', query_sql)
    ret = cursor.execute(query_sql)
    with open(f'{table_name} {today}.txt', 'a+', encoding='utf-8') as f:
        for path_info in ret.fetchall():
            print(f'[+] 正在导出 => {path_info[0]} * 计数 => {path_info[1]}')
            f.write(f'{path_info[0]}\n')
    cursor.close()
    conn.close()
    print(f'导出完成')


if __name__ == '__main__':
    select_path_from('php_dir', 8311)
