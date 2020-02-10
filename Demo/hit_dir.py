import sqlite3
from collections import Counter
import requests

hit_dict = {}
hit_list = []

with open('hit_test.txt', 'r', encoding='utf-8') as f:
    for dir_name in f:
        dir_name = dir_name.strip('\n')
        url = f'http://140.143.230.35/{dir_name}'
        print(url)
        r = requests.get(url)
        if r.status_code == 200:
            hit_list.append(dir_name)

print(hit_list)
hits = Counter(hit_list)
print(hits['phpinfo.php'])
print(type(hits['phpinfo.php']))


def update_sqlite_count(file_type):
    conn = sqlite3.connect('all_dict.db')
    cursor = conn.cursor()
    # query_sql = f"update dir_file FROM {file_type}_dir_file;"
    query_sql = "SELECT count FROM php_dict WHERE dir_file ='static';"
    print(query_sql)
    cursor.execute(query_sql)
    # print(cursor.fetchall())
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    update_sqlite_count('php')