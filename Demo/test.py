import sqlite3

conn = sqlite3.connect('test.db')
cursor=conn.cursor()

# cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')

# cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
print(cursor.rowcount)
print(cursor.execute('select * from user where id=?', ('1',)))