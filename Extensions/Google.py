import time
from tqdm import trange
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    page_ended = False
    while not page_ended:
        driver.execute_script(f"window.scrollTo(0, {last_height});")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            page_ended = True
        else:
            last_height = new_height

        try:
            driver.find_element(By.CLASS_NAME, "LZ4I").click()
        except Exception:
            pass

def scrape_images_from_google(query: str, limit: int = None) -> list[str]:
    img_srcs = set()
    if "http" in query:
        page_url = query
    else:
        page_url = "https://www.google.com/search?q={}&source=lnms&tbm=isch&safe=off".format(query.replace(" ", "+"))
    
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(page_url)
        time.sleep(1)

        scroll_to_bottom(driver)

        thumbnails = driver.find_elements(By.XPATH, "//img[@class='rg_i Q4LuWd']")

        if limit is not None:
            limit = min(limit, len(thumbnails))
        else:
            limit = len(thumbnails)

        for i in trange(limit, desc="Extracting images", unit=" images"):
            try:
                driver.execute_script("arguments[0].click();", thumbnails[i])
                time.sleep(1)

                image = wait.until(EC.presence_of_element_located((By.XPATH, "//img[@class='sFlh5c pT0Scc']")))
                src = image.get_attribute('src')
                if src:
                    img_srcs.add(src)

            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return img_srcs