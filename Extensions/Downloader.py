import os
import asyncio
import aiohttp
from tqdm import tqdm
from uuid import uuid4
from hashlib import sha256
from Extensions.Database import fetch_data, batch_insert, batch_update

os.makedirs('Downloads', exist_ok=True)
hashes_dict = {hash.strip(): 1 for hash in open(r'Support files\hashes.txt', 'r').readlines()}
semaphore = asyncio.Semaphore(100)

def guess_file_type(url, response):
    img_types = ['jpeg', 'jpg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico', 'tiff']
    ext = os.path.splitext(url)[1][1:].lower()
    if ext in img_types:
        return ext
    return response.headers.get('Content-Type', "nope/nope").split("/")[1] if '/' in response.headers.get('Content-Type') else 'jpg'


async def download(session, url, statuses, bar):
    async with semaphore:
        try:
            async with session.get(url) as response:
                content = await response.read()
                hash_val = sha256(content).hexdigest()

                if hash_val not in hashes_dict:
                    filetype = guess_file_type(url, response)
                    filename = f'{uuid4().hex}.{filetype}'
                    with open(os.path.join('Downloads', filename), 'wb') as file:
                        file.write(content)
                    hashes_dict[hash_val] = 0
                    statuses[url] = 'success'
                else:
                    hashes_dict[hash_val] += 1
                    statuses[url] = 'duplicate'
                
        except Exception as e:
            statuses[url] = 'failed'

        finally:
            bar.update(1)


async def Downloader(FETCH_LENGTH:int=0, links=None):
    async with aiohttp.ClientSession() as session:
        if links is None:
            statuses = fetch_data(FETCH_LENGTH)  # returns dict
        else:
            statuses = {link: 'pending' for link in links}
            batch_insert(statuses)

        bar = tqdm(desc='Downloading', total=len(statuses), unit=' images', position=0)

        tasks = [download(session, url, statuses, bar) for url in statuses.keys()]
        await asyncio.gather(*tasks)
        bar.close()

        batch_update(statuses)

        hashes = [key for key, value in hashes_dict.items() if value > 0]
        with open(r'Support files\hashes.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(hashes))

        print('\nTotal Success:', list(statuses.values()).count('success'))
        print('Total Duplicate:', list(statuses.values()).count('duplicate'))
        print('Total Failed:', list(statuses.values()).count('failed'))

def start(n, links=None):
    asyncio.run(Downloader(n, links))
