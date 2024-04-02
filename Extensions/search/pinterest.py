from sys import exit
import json
import yaml
import os.path
import argparse

if __name__ == "__main__":
    currentdir = os.getcwd()
    parser = argparse.ArgumentParser(description='An infinite pinterest crawler. Auther: mirusu400')

    parser.add_argument('-d', '--directory', required=False, default="", help='Directory you want to download')
    parser.add_argument('-l', '--link', required=False, default="", help='Link of Pinterest which you want to scrape')
    parser.add_argument('-g', '--page', required=False, default="", help='Number of pages which you want to scrape')
    parser.add_argument('-b', '--batch', required=False, default=False, action="store_true", help='Enable batch mode (Please read README.md!!)')
    args = parser.parse_args()

    email = args.email
    password = args.password
    directory = args.directory
    link = args.link
    pages = args.page
    batch = args.batch
    
    yaml_email = ""
    yaml_password = ""
    yaml_directory = ""
    
    # Check yaml exists
    if os.path.isfile(currentdir + "/config.yaml"):
        with open("./config.yaml", "r") as f:
            config = yaml.load(f)
            yaml_email = config["email"]
            yaml_password = config["password"]
            yaml_directory = config["directory"]

    if email == "":
        if yaml_email != "":
            email = yaml_email
        else: 
            email = input("Enter your email: ")

    if password == "":
        if yaml_password:
            password = yaml_password
        else: 
            password = input("Enter your password: ")
    
    dir_list = []
    link_list = []
    if batch != False:
        print("Batch mode Enabled. You will download a bunch of Images..")
        if not os.path.exists(currentdir + "/batch.json"):
            print("Batch.json file not found! Please read README.md...")
            exit()
        batch_list = json.loads(open(currentdir + "/batch.json").read())
        for item in batch_list:
            dir_list.append(item["dir"])
            link_list.append(item["link"])
    else:
        if directory == "":
            if yaml_directory:
                directory = yaml_directory
            else: 
                directory = input("Enter the directory to save the images (Blank if you set default): ")
        if directory == "":
            directory = "download"

        if link == "":
            link = input("Enter the link to scrape (Blank if default; Pinterest main page): ")
        if link == "":
            link = "https://pinterest.com/"

    if pages == "":
        page = input("Enter the number of pages to scrape (Blank if infinity): ")
    if pages == "" or int(pages) == 0:
        pages = 999999
    else:
        pages = int(pages)

    p = Pinterest(email, password)

    if batch == False:
        print("Download Image")
        p.single_download(pages, link, directory)
    
    else:
        print("Download Image in Batch mode...")
        p.batch_download(pages, link_list, dir_list)

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
from sys import exit
import asyncio
import os
import pickle

class EndPageException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "End of page"
    
import requests
import asyncio
from time import sleep

async def download_image(src, dir, i):
    ErrorLevel = 0
    failed = False
    filename = src.split('/')[-1]
    if dir[-1] != "/":
        dir += "/"
    savedir = dir + filename
    src = src.replace("/236x/", "/originals/").replace("/474x/", "/originals/").replace("/736x/", "/originals/")
    while True:
        try:
            request = requests.get(src)
            # If status code is not 200, skip this image
            # Maybe this cause 403 Error, but I don't know how to handle it
            # assert request.status_code == 200
            if request.status_code != 200:
                print(f"Download {src} fail!")
                return True
           
            with open(savedir, 'wb') as file:
                file.write(request.content)
            print(f"Download {src} done!")
            break
        except Exception as e:
            print(f"{src} : Download fail! Error: {e}")
            ErrorLevel += 1
            sleep(1)
            if (ErrorLevel >= 10):
                failed = True
                print(src + ": Download fail, Skip image")
                break
    return failed


async def download_image_host(plist, dir):
    fail_image = 0
    fts = [asyncio.ensure_future(download_image(plist[i], dir, i)) for i in range(0, len(plist))]
    fail_image = await asyncio.gather(*fts)
    return fail_image

class Pinterest():
    def __init__(self, login, pw):
        self.domains = [".pinterest.com", ".www.pinterest.com", "www.pinterest.com", ".www.pinterest.co.kr", "www.pinterest.co.kr"]
        self.piclist = []
        self.currentdir = os.getcwd()
        self.user_agent = ""
        options = webdriver.EdgeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Edge(options=options)
        self.user_agent = self.driver.execute_script("return navigator.userAgent;")
        if os.path.exists("cookies.pkl"):
            print("Loading cookies...")
            self.driver.get("https://pinterest.com")
            self.driver.implicitly_wait(3)
            sleep(2)
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                # print(cookie)
                for domain in self.domains:
                    try:
                        self.driver.add_cookie({
                            "domain": domain,
                            "name": cookie["name"],
                            "value": cookie["value"],
                            "path": '/'
                            # "expiry": None
                        })
                    except:
                        pass
            self.driver.get("https://pinterest.com")
            self.driver.implicitly_wait(3)
            try:
                self.driver.find_element(By.XPATH, '//*[@id="HeaderContent"]')
                return
            except:
                print("Failed to login from cookies.. login manually")
                # input()
                # pass
        try:
            self.driver.get("https://pinterest.com/login")
            self.driver.implicitly_wait(3)
            for i in range(3):
                try:
                    self.driver.find_element(By.ID, "email")
                    break
                except:
                    sleep(1)
            emailelem = self.driver.find_element(By.ID, "email")
            passelem = self.driver.find_element(By.ID, "password")
            emailelem.send_keys(login)
            passelem.send_keys(pw)
            sleep(1)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except Exception as e:
            raise e
        
        while True:
            try:
                self.driver.find_element(By.XPATH, '//*[@id="HeaderContent"]')
                break
            except:
                sleep(1)
                try:
                    self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
                except:
                    pass
        self.dump()
        return

    def dump(self):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open("cookies.pkl","wb"))

    def crawl(self, dir):
        timeout = 0
        height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            now_height = self.driver.execute_script("return document.body.scrollHeight")

            # If height changed
            if now_height != height:
                self.download_image(dir)
                break
            else:
                timeout += 1
                if timeout >= 5:
                    print("It seems we find the end of current page, stop crawling.")
                    raise EndPageException('End!')
        sleep(2)
        return
    
    def single_download(self, n=-1, url="https://pinterest.com/", dir="./download"):
        global loop
        fail_image = 0
        if n == -1:
            n = 999999999
        loop = asyncio.get_event_loop()

        # Create directory
        if dir[0] == "/":
            dir = dir[1:]
        directory = os.path.join(self.currentdir, dir)
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        self.driver.get(url)
        self.driver.implicitly_wait(3)
        for i in range(n):
            if len(self.piclist) > 500:
                return
            try:
                self.crawl(dir)
            except EndPageException as e:
                break
            print(f"Scroll down {i} Page, downloaded {len(self.piclist)} images.")
        download_pic_count = len(self.piclist)
        print(f"Totally downloaded {download_pic_count} images.")
        loop.close
        return fail_image
    
    def batch_download(self, n=-1, url_list = [], dir_list = [], dir="./download"):
        global loop
        loop = asyncio.get_event_loop()
        url_count = len(url_list)
        dir_count = len(dir_list)
        if n == -1:
            n = 9999999
        if dir_list != [] and url_count != dir_count:
            print("url_list and dir_list must have same length.")
            exit()

        # Open all tabs
        for i in range(url_count-1):
            self.driver.execute_script("window.open('','_blank');")

        for i in range(url_count):
            self.driver.switch_to.window(self.driver.window_handles[i])
            self.driver.get(url_list[i])
            self.driver.implicitly_wait(3)

        for i in range(0,n):
            for uindex in range(url_count):
                dir = dir_list[uindex] if dir_count != 0 else dir

                if dir[0] == "/":
                    dir = dir[1:]
                dir = os.path.join(self.currentdir, dir)
                if not os.path.exists(dir):
                    os.mkdir(dir)
                
                try:
                    self.driver.switch_to.window(self.driver.window_handles[uindex])
                except:
                    continue

                download_pic_count = len(self.piclist)

                try:
                    self.crawl(dir)
                except EndPageException as e:
                    del url_list[uindex]
                    del dir_list[uindex]
                    self.driver.close()
                    url_count -= 1
                    dir_count -= 1

                print(f"Scroll down from {url_list[uindex]}, {i} Page, downloaded {download_pic_count} images.")

        return


    def download_image(self, dir="./download"):
        page_pic_list=[]
        req = self.driver.page_source
        soup = BeautifulSoup(req, 'html.parser')
        pics = soup.find_all("img")
        if pics is None:
            return 0
        for pic in pics:
            src = pic.get("src")
            
            # Profile image, skip
            if "75x75_RS" in src:
                continue

            if src not in self.piclist:
                self.piclist.append(src)
                page_pic_list.append(src)
        
        fail_image = sum(loop.run_until_complete(download_image_host(page_pic_list,dir)))
        return fail_image

    
    def getdriver(self):
        return self.driver