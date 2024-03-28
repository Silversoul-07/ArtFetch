import threading
import sqlite3
import os
from fake_useragent import UserAgent
from hashlib import sha256
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from urllib3 import PoolManager, Timeout
from PIL import Image
import io
import numpy as np

FETCH_LENGTH = 100

class Downloader:
    def __init__(self):
        tqdm.write('Init Program...')
        self.user_agent = UserAgent()
        self.entries = []
        self.lock = threading.Lock() 
        self.http = PoolManager(timeout=Timeout(total=10))
        self.hashes = open(r'data\hashes.txt', 'r').read().splitlines()
        self.bar = tqdm(desc='Downloading', unit=' images', position=0) 
        # self.model = load_model('model.keras')
        tqdm.write('Init Successful!')

    def guess_file_type(self, url, response):
        img_types = ['jpeg', 'jpg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico', 'tiff']
        ext = os.path.splitext(url)[1][1:]
        if ext in img_types:
            return ext
        return response.headers.get('Content-Type', "nope/nope").split("/")[1] if '/' in response.headers.get('Content-Type') else 'jpg'

    def download(self, url):
        headers = {'User-Agent': self.user_agent.random}
        try:
            with self.http.request('GET', url, headers=headers, preload_content=False) as r:
                content = r.data
                hash = sha256(content).hexdigest()

                with self.lock:  
                    if hash not in self.hashes:
                        filetype = self.guess_file_type(url, r)
                        filename = f'{uuid4().hex}.{filetype}'
                        with Image.open(io.BytesIO(content)) as img:
                            img.save(os.path.join('downloads', filename), format=filetype)

                        self.entries.append([url, 'success'])
                        self.hashes.append(hash)
                    else:
                        self.entries.append([url, 'duplicate'])

        except Exception as e:
            with self.lock: 
                self.entries.append([url, 'failed'])
        finally:
            with self.lock:
                self.bar.update(1) if self.bar else None

    def batch_update(self, values):
        with sqlite3.connect(r'database\data.db') as conn:
            cursor = conn.cursor()
            for url, status in values:
                cursor.execute('UPDATE data SET status=? WHERE link=?', (status, url))
            conn.commit()

    def batch_insert(self, values):
        with sqlite3.connect(r'database\data.db') as conn:
            cursor = conn.cursor()
            for url, status in values:
                cursor.execute('INSERT INTO data (link, status) VALUES (?, ?)', (url, status))
            conn.commit()

    def fetch_data(self):
        with sqlite3.connect(r'database\data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT link FROM data WHERE status IS "pending" ORDER BY sno LIMIT ?', (FETCH_LENGTH,))
            return [row[0] for row in cursor.fetchall()]
    
    def predict(self, image_path):
        img = Image.open(image_path)
        img = img.resize((180, 180))
        img = np.expand_dims(img, axis=0)
        img = img/255
        prediction = self.model.predict(img)
        return np.argmax(prediction)
        
    def sort_data(self):
        '''Models classifies the images and sorts them into respective folders'''   
        for image in os.listdir('images'):
            image_path = os.path.join('images', image)
            prediction = self.predict(image_path)
            if prediction == 0:
                os.rename(image_path, os.path.join('images', 'like', image))
            else:
                os.rename(image_path, os.path.join('images', 'dislike', image))

    
    def start(self, links=None):
        if links is None:
            links = self.fetch_data() 
        else:
            self.batch_insert([[link, 'pending'] for link in links])
                
        self.bar.total = len(links) 

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self.download, links)

        self.batch_update(self.entries)
        tqdm.write('Updated')

        freq_dist = dict()

        for i in self.hashes:
            if hash not in freq_dist:
                freq_dist[hash] = 1
            else:
                freq_dist[hash] += 1

        required = [k for k,v in freq_dist.items() if v > 1]

        with open('hashes.txt', 'w', encoding='utf-8') as f:
            for i in required:
                f.write(i + '\n')
            
        
        self.bar.close()
