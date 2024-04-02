from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from tqdm import trange

def scrape_data_from_aznude(url, limit):
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Edge()
    driver.get()

    srcs = []
    movie = driver.find_elements(By.CLASS_NAME, 'movie')

    if limit is not None:
        limit = min(limit, len(movie))
    else:
        limit = len(movie)
    
    for i in trange(limit, desc="Extracting images", unit=" images"):
        driver.execute_script("arguments[0].click();", movie[i])
        try:

            iframe = driver.find_elements(By.CSS_SELECTOR, 'div.mfp-content > div > iframe')

            if len(iframe) > 0:
                driver.switch_to.frame(iframe[0])
                video = driver.find_element(By.CSS_SELECTOR, 'div.jw-media.jw-reset > video')
                srcs.append(video.get_attribute('src'))
                driver.switch_to.default_content()
                close = driver.find_element(By.CSS_SELECTOR, 'button.mfp-close')
                driver.execute_script("arguments[0].click();", close)
            else:
                img = driver.find_element(By.CSS_SELECTOR, 'img.mfp-img')
                srcs.append(img.get_attribute('src'))
                close = driver.find_element(By.CSS_SELECTOR, 'button.mfp-close')
                driver.execute_script("arguments[0].click();", close)

        except Exception as e:
            print("Error occured at", i, e)
            break

    driver.quit()

    return srcs