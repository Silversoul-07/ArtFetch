import os
import asyncio
import aiohttp
import base64
from tqdm import tqdm
from uuid import uuid4
from hashlib import sha256
from Extensions.Download.Database import fetch_data, batch_insert, batch_update

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
        if links is None:
            statuses = fetch_data(fetch_length)  # returns dict
        else:
            links = set(links)
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

def Downloader(n=0, links=None):
    asyncio.run(main(n, links))
