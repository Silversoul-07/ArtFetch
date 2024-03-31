import time
from tqdm import trange
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
options = webdriver.EdgeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 10)

query = input("Enter the query: ")
url = f"http://www.bing.com/images/search?q={query.replace(' ', '+')}"
url
driver.get(url)

driver = webdriver.Edge()
soup = BeautifulSoup(driver.page_source, 'html.parser')
img = [json.loads(i.get('data-m'))['murl'] for i in soup.find_all('a', class_='richImgLnk')]
len(img)
with open('links.txt','a+',encoding='utf-8') as f:
    for i in img:
        f.write(i+'\n')