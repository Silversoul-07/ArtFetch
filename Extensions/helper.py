import os
import time
import json
from urllib.parse import urlparse
from PIL import Image
from nudenet import NudeDetector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import cv2
from os import listdir, rename 
from os.path import join
from tqdm.notebook import tqdm

def remove_small_images(dir):
    min_width = 600  # Define your minimum width threshold
    min_height = 400  # Define your minimum height threshold
    sub_dir = join(dir, "small")
    bar = tqdm(total=len(listdir(dir)), desc="Removing small images")
    for file in listdir(dir):
        try:
            path = join(dir, file)
            height, width, _ = cv2.imread(path).shape
            if height < min_height and width < min_width:
                rename(path, join(sub_dir,file))
        except: 
            pass
        finally:
            bar.update(1)

def isCorrupt_Image(dir):
    '''Checks if the images in the directory are corrupt'''
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        try: 
            Image.open(path).verify()
        except (IOError, SyntaxError) as e:
            os.remove(path)

class GenderClassifier:
    '''On Init it automatically classifies the images into male and female'''
    def __init__(self, dir):
        self.detector = NudeDetector()
        self.female = ['FEMALE_GENITALIA_COVERED', 'FACE_FEMALE', 'BUTTOCKS_EXPOSED', 'FEMALE_BREAST_EXPOSED', 'FEMALE_GENITALIA_EXPOSED', 'FEET_EXPOSED', 'BELLY_COVERED', 'FEET_COVERED', 'ARMPITS_COVERED', 'ARMPITS_EXPOSED', 'FEMALE_BREAST_COVERED', 'BUTTOCKS_COVERED', 'BELLY_EXPOSED ']
        self.male = ['MALE_BREAST_EXPOSED', 'ANUS_EXPOSED', 'FACE_MALE', 'MALE_GENITALIA_EXPOSED', 'ANUS_COVERED']
        if dir is not None:
            os.makedirs(os.path.join(dir, 'male'), exist_ok=True)
            os.makedirs(os.path.join(dir, 'female'), exist_ok=True)
            self.classify_and_move_files(dir)

    def classify_gender(self, result):
        average = []
        for item in result:
            if item['class'] in self.male:
                average.append('male')
            elif item['class'] in self.female:
                average.append('female')
        return max(set(average), key=average.count) if average else None

    def classify_and_move_files(self, directory):
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            try:
                result = self.detector.detect(path)
                gender = self.classify_gender(result)
                if gender is not None:
                    os.rename(path, os.path.join(gender, filename))
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

class WebDriverHelper:
    def __init__(self):
        pass
        
    def get_webdriver(self, headless, driver_path = "Support files//msedgedriver.exe"):
        service = Service(executable_path=driver_path) if driver_path else None
        options = webdriver.EdgeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")
        if headless:
            options.add_argument("--headless")
        return webdriver.Edge(options=options, service=service)

    def scroll_to_bottom(self, driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script(f"window.scrollTo(0, {last_height});")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if last_height == new_height:
                break
            last_height = new_height

            try:
                driver.find_element(By.CLASS_NAME, "LZ4I").click()
            except Exception:
                pass

class LinkHelper:
    def __init__(self, file_path='Support files\\sorted_links.json'):
        self.file_path = file_path

    def _load_links(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _save_links(self, categories):
        with open(self.file_path, 'w') as f:
            json.dump(categories, f)

    def classify_links(self, links):
        categories = self._load_links()
        errors = 0

        for link in links:
            try:
                domain = 'base64' if link.startswith('data:image') else '.'.join(urlparse(link).netloc.split('.')[-2:])
            except Exception:
                errors += 1
                continue

            if domain in categories:
                categories[domain].append(link)
            else:
                categories[domain] = [link]

        self._save_links(categories)
        print(f'Errors: {errors}')

    def extract_specific_links(self, domain):
        categories = self._load_links()
        return categories.get(domain, [])

    def extract_all_links(self):
        return self._load_links()

    def delete_links(self, domain):
        categories = self._load_links()
        if domain in categories:
            del categories[domain]
        self._save_links(categories)
        print(f'Deleted {domain}')

    def delete_all_links(self):
        self._save_links({})
        print('Deleted all links')

from keras import load_model

class Grouper:
    def __init__(self) -> None:
        self.model = load_model('model.keras')

    def predict(self, image_path):
        pass
        
    def start(self):
        '''Models classifies the images and sorts them into respective folders'''   
        for image in os.listdir('images'):
            image_path = os.path.join('images', image)
            prediction = self.predict(image_path)
            if prediction == 0:
                os.rename(image_path, os.path.join('images', 'like', image))
            else:
                os.rename(image_path, os.path.join('images', 'dislike', image))