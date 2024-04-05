import os
import sqlite3   

os.makedirs('Support files', exist_ok=True)

DATABASE = r'Support files\data.db'

def create_table():
    with sqlite3.connect(DATABASE) as conn:
        conn = conn.cursor()
        conn.execute('CREATE TABLE IF NOT EXISTS data (sno INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, status TEXT)')

def is_exists(links:list[str]) -> dict[str, str]:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        existing_links = {}
        for link in links:
            cursor.execute('SELECT link FROM data WHERE link = ?', (link,))
            result = cursor.fetchone()
            if result:
                existing_links[link] = 'exists'
            else:
                existing_links[link] = 'new'
        return existing_links

def fetch_data(n):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT link,status FROM data WHERE status IS "failed" ORDER BY sno LIMIT ?', (n,))
        return {row[0]:row[1] for row in cursor.fetchall()}
    
def fetch_all_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT link,status FROM data WHERE status IS "failed"')
        return {row[0]:row[1] for row in cursor.fetchall()}
        
def batch_insert(values:dict):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for url, status in values.items():
            cursor.execute('INSERT INTO data (link, status) VALUES (?, ?)', (url, status))
        conn.commit()
    print("Inserted into Database Successfully!")   

def batch_update(values:dict):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for url, status in values.items():
            cursor.execute('UPDATE data SET status=? WHERE link=?', (status, url))
        conn.commit()
    print("Updated Database Successfully!")

if not os.path.exists(DATABASE):
    create_table()