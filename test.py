from time import sleep
import certifi
import pymongo
import sys
import os
import argparse
from bson.json_util import dumps, loads
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
import undetected_chromedriver.v2 as uc

parser = argparse.ArgumentParser(description='Insert data to mongdb.net')
parser.add_argument("--con", help="Connection url", default="")
args = parser.parse_args()


client = pymongo.MongoClient(args.con, tlsCAFile=certifi.where())
mydb = client["mydb"]
mycol = mydb["links"]
x = mycol.find_one({})
if x is None:
    print("None")
    quit()
info = loads(dumps(x))
mycol.update_one(x, { "$set": { 'page':int(info['page'])+1 } })  
url = info['link']+str(int(info['page']))

display = Display(visible=0, size=(1024, 768))
display.start()

chrome_options = uc.ChromeOptions()
#chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=1024,768")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--user-data-dir=/root/chrome')
chrome_options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = uc.Chrome(options=chrome_options)
#driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver)
driver.get(url)
#driver.implicitly_wait(5)
#print(driver.title)
#quit()

videos=driver.find_element(By.CSS_SELECTOR('a.thumb'))
links=[]
for index,video in enumerate(videos):
    href=video.get_attribute('href')
    print(href)
    links.append(href)

tasks=[]
for index,link in enumerate(links):
    task = {}
    name=link.split('/')[-1].replace('_watch-online','')+'.mp4'
    task['link']=link
    task['name']=name
    driver.get(link)
    driver.implicitly_wait(5)
    shodiv=driver.find_element(By.CSS_SELECTOR('button#showdiv'))
    ActionChains(driver).click(shodiv).perform()
    driver.implicitly_wait(1)
    btn=driver.find_element(By.XPATH, '//a[contains(text(),"AC")]')
    if btn is None:
        continue
    ActionChains(driver).click(btn).perform()
    driver.implicitly_wait(2)
    windows = driver.window_handles
    driver.switch_to.window(windows[1])
    driver.implicitly_wait(2)
    button=driver.find_element(By.XPATH, '//button[contains(text(),"DOWNLOAD")]')
    ActionChains(driver).click(button).perform()
    if index ==0:
        driver.implicitly_wait(2)
        driver.switch_to.window(windows[1])
        button=driver.find_element(By.XPATH, '//button[contains(text(),"DOWNLOAD")]')
        ActionChains(driver).click(button).perform()
    driver.implicitly_wait(2)
    task['downloadlink']=driver.current_url
    tasks.append(task)
    print(task)
    windows = driver.window_handles
    for index,window in enumerate(windows):
        if index>0:
            driver.switch_to.window(window)
            driver.close()
    driver.switch_to.window(windows[0])
    continue
driver.quit()


taskscol = mydb["tasks"]
for task in tasks:
    saveurl=task['downloadlink']+'##'+task['name']
    mydict = { "url": saveurl, "isnow": '0'}    
    taskscol.insert_one(mydict) 

quit()
