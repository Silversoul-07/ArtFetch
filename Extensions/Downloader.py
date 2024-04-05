import os
import asyncio
import aiohttp
import base64
from tqdm import tqdm
from uuid import uuid4
from hashlib import sha256

import os
import sqlite3   

class Database:
    def __init__(self, database:str = r'Support files\data.db'):
        self.database = self.get_table()

    def get_table(self):
        with sqlite3.connect(self.database) as conn:
            conn = conn.cursor()
            if not os.path.exists(self.database):
                conn.execute('''CREATE TABLE IF NOT EXISTS data 
                            (sno INTEGER PRIMARY KEY AUTOINCREMENT, 
                            link TEXT, 
                            status TEXT)''')
                return 
            else:
                return

    def is_exists(self, links:list[str]) -> dict[str, str]:
        with sqlite3.connect(self.database) as conn:
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

    def fetch_data(self, n):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT link,status FROM data WHERE status IS "failed" ORDER BY sno LIMIT ?', (n,))
            return {row[0]:row[1] for row in cursor.fetchall()}
        
    def fetch_all_data(self):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT link,status FROM data WHERE status IS "failed"')
            return {row[0]:row[1] for row in cursor.fetchall()}
            
    def batch_insert(self, values:dict):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            for url, status in values.items():
                cursor.execute('INSERT INTO data (link, status) VALUES (?, ?)', (url, status))
            conn.commit()
        print("Inserted into self.database Successfully!")   

    def batch_update(self, values:dict):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            for url, status in values.items():
                cursor.execute('UPDATE data SET status=? WHERE link=?', (status, url))
            conn.commit()
        print("Updated self.database Successfully!")


os.makedirs('Downloads', exist_ok=True)
hashes_dict = {hash.strip(): 1 for hash in open(r'Support files\hashes.txt', 'r').readlines()}
image_types = {'jpeg', 'jpg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico', 'tiff'}
semaphore = asyncio.Semaphore(100)

class InvalidURLError(Exception):
    def __init__(self, message):
        super().__init__(message)


def guess_file_type(url, response=None):
    ext = os.path.splitext(url)[1][1:].lower()
    
    if ext in image_types:
        return ext
    elif response is not None and '/' in response.headers.get('Content-Type', ''):
        return response.headers.get('Content-Type').split('/')[-1]
    else:
        return 'jpg'

def decoder(data_uri):
    try:
        header, data = data_uri.split(',', 1)
        encoded_data = data.encode()
        
        for image_type in image_types:
            if image_type in header:
                return image_type, base64.b64decode(encoded_data)
        
        return 'jpg', base64.b64decode(encoded_data)
    except Exception:
        return None


def write_file(content, filename):
    with open(os.path.join('Downloads', filename), 'wb') as file:
        file.write(content)



async def download(session, url, statuses, bar, semaphore, hashes_dict):
    async with semaphore:
        try:
            if url.startswith('data:image'):
                raise InvalidURLError('Invalid URL')

            async with session.get(url) as response:
                content = await response.read()
                hash_val = sha256(content).hexdigest()

                if hash_val not in hashes_dict:
                    filename = f'{uuid4().hex}.{guess_file_type(url, response)}'
                    write_file(content, filename)
                    hashes_dict[hash_val] = 0
                    statuses[url] = 'success'
                else:
                    hashes_dict[hash_val] += 1
                    statuses[url] = 'duplicate'

        except InvalidURLError:
            filetype, content = decoder(url)
            if content is not None:
                hash_val = sha256(content).hexdigest()
                if hash_val not in hashes_dict:
                    filename = f'{uuid4().hex}.{filetype}'
                    write_file(content, filename)
                    hashes_dict[hash_val] = 0
                    statuses[url] = 'success'
                else:
                    hashes_dict[hash_val] += 1
                    statuses[url] = 'duplicate'
        except Exception as e:
            statuses[url] = 'failed'
        finally:
            bar.update(1)


async def main(fetch_length, links):
    async with aiohttp.ClientSession() as session:

        if links is None and fetch_length == 0:
            statuses = fetch_all_data()
        elif links is None:
            statuses = fetch_data(fetch_length)  # returns dict
        else:
            links = set(links)
            statuses = {link: 'pending' for link in links}
            batch_insert(statuses)

        bar = tqdm(desc='Downloading', total=len(statuses), unit=' images', position=0)

        tasks = [download(session, url, statuses, bar, semaphore, hashes_dict) for url in statuses.keys()]
        await asyncio.gather(*tasks)
        bar.close()

        batch_update(statuses)

        hashes = [key for key, value in hashes_dict.items() if value > 0]
        with open(r'Support files\hashes.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(hashes))

        print('\nTotal Success:', list(statuses.values()).count('success'))
        print('Total Duplicate:', list(statuses.values()).count('duplicate'))
        print('Total Failed:', list(statuses.values()).count('failed'))

def Downloader(n=0, links=None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(n, links))
