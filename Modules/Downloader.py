import os
import asyncio
import aiohttp
from tqdm import tqdm
from uuid import uuid4
from hashlib import sha256
from Modules.Database import fetch_data, batch_insert, batch_update

FETCH_LENGTH = 500
os.makedirs('Downloads', exist_ok=True)
hashes = set(open(r'Resources\hashes.txt', 'r').read().splitlines())
new_hashes = set(open(r'new_hashes.txt', 'r').read().splitlines())
semaphore = asyncio.Semaphore(20)

def guess_file_type(url, response):
    img_types = ['jpeg', 'jpg', 'png', 'gif', 'svg', 'webp', 'bmp', 'ico', 'tiff']
    ext = os.path.splitext(url)[1][1:]
    if ext in img_types:
        return ext
    return response.headers.get('Content-Type', "nope/nope").split("/")[1] if '/' in response.headers.get('Content-Type') else 'jpg'


async def download(session, url, statuses, bar):
    async with semaphore:
        try:
            async with session.get(url) as response:
                content = await response.read()
                hash_val = sha256(content).hexdigest()

                if hash_val not in hashes:
                    filetype = guess_file_type(url, response)
                    filename = f'{uuid4().hex}.{filetype}'
                    with open(os.path.join('Downloads', filename), 'wb') as file:
                        file.write(content)

                    statuses[url] = 'success'
                else:
                    statuses[url] = 'duplicate'
                    new_hashes.add(hash_val)

        except Exception as e:
            statuses[url] = 'failed'

        finally:
            bar.update(1)


async def Downloader(links=None):
    async with aiohttp.ClientSession() as session:
        if links is None:
            statuses = fetch_data(FETCH_LENGTH)  # returns dict
        else:
            statuses = {link: 'pending' for link in links}
            batch_insert(statuses)

        bar = tqdm(desc='Downloading', total=len(statuses), unit=' images', position=0)

        tasks = [download(session, url, statuses, bar) for url in statuses.keys()]
        await asyncio.gather(*tasks)

        batch_update(statuses)

        open('new_hashes.txt','w').write('\n'.join(new_hashes))

        bar.close()

def start(links=None):
    asyncio.run(Downloader(links))
