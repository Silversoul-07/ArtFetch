from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


def get_webdriver(headless=True):
    service = Service(executable_path="Support files//msedgedriver.exe")
    options = webdriver.EdgeOptions()
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("--log-level=3")
    if headless:
        options.add_argument("--headless")
    return webdriver.Edge(options=options, service=service)

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
