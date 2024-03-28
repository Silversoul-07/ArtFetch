from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
from fake_useragent import UserAgent
import os
import concurrent.futures
from tqdm import tqdm

def download(link):
        try:
            img_obj = requests.get(link.attrs["href"])
            title = link.attrs["href"].split("/")[-1]
            try:
                img = Image.open(BytesIO(img_obj.content))
                img.save(os.path.join(dir,title), img.format)
            except:
                pass
        except:
            pass

def BingSearch(topic, dir):
    headers = {'User-Agent': UserAgent().random}
    params = {"q": topic}

    r = requests.get("http://www.bing.com/images/search", params=params, headers=headers)
    if not r.ok:
        print('Connection Failed!')
        return
    else:
        print('Connection ok')

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", {"class": "thumb"})

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        list(tqdm(executor.map(download, links), total=len(links)))

if __name__ == "__main__":
    BingSearch(
        topic = "Hot images of Tamil girl",
        dir = "downloads",
    )

from bs4 import BeautifulSoup
from selenium import webdriver
import json

driver = webdriver.Edge()
soup = BeautifulSoup(driver.page_source, 'html.parser')
img = [json.loads(i.get('data-m'))['murl'] for i in soup.find_all('a', class_='richImgLnk')]
len(img)
with open('links.txt','a+',encoding='utf-8') as f:
    for i in img:
        f.write(i+'\n')