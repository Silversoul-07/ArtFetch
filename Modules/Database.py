import os
import sqlite3   
        
os.makedirs('Resources', exist_ok=True)

DATABASE = r'Resources\data.db'

def create_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
        '''CREATE TABLE data(
            link VARCHAR2(),
            status VARCHAR2()
            )'''
        )

def fetch_data(n):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT link,status FROM data WHERE status IS "pending" ORDER BY sno LIMIT ?', (n,))
        return {row[0]:row[1] for row in cursor.fetchall()}
        
def batch_insert(values:dict):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for url, status in values.items():
            cursor.execute('INSERT INTO data (link, status) VALUES (?, ?)', (url, status))
        conn.commit()

def batch_update(values:dict):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for url, status in values.items():
            cursor.execute('UPDATE data SET status=? WHERE link=?', (status, url))
        conn.commit()

if __name__ == "__main__":
    test = fetch_data(10)
    print(type(test))
    print(test)