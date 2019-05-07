from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from PIL import Image
from io import BytesIO
import requests
import os
from tqdm import tqdm
import base64
import time

CHROME_DRIVER = './driver/chromedriver_win.exe'
keyword = 'cat'
BROWSER_URLS = {'bing': 'https://www.bing.com/images/search?q={0}',
                'naver': 'https://search.naver.com/search.naver?where=image&sm=tab_jum&query={0}',
                'google': 'https://www.google.co.kr/search?q={0}&source=lnms&tbm=isch'}
BROWSER_MAGIC_WORDS = {'bing': 'mimg', 'naver': '_img', 'google': 'rg_ic'}
BROWSER_MORE_BUTTON = {'bing': '', 'naver': '//a[@class="btn_more _more"]', 'google': '//input[@id="smb"]'}

def _get_links(keyword, driver_location=CHROME_DRIVER, scroll_num=60, search_engine='google'):
    browser = webdriver.Chrome(driver_location)
    browser.get(BROWSER_URLS[search_engine].format(keyword))

    body = browser.find_element_by_tag_name('body')

    while True:
        for i in tqdm(range(scroll_num), desc='scrolling page'):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)
        try:
            WebDriverWait(browser, 1).until(expected_conditions.element_to_be_clickable((By.XPATH, BROWSER_MORE_BUTTON[search_engine]))).click()
        except TimeoutException:
            break

    keys = browser.find_elements_by_class_name(BROWSER_MAGIC_WORDS[search_engine])
    links = []
    for key in keys:
        link = key.get_attribute('src')
        if link is None:
            link = key.get_attribute('data-src')
        links.append(link)

    browser.close()
    return links

def _get_images_from_link(links, save_dir='./test'):
    if os.path.isdir(save_dir) is False:
        os.makedirs(save_dir)

    for i, link in tqdm(enumerate(links), desc='getting images from link'):
        print(link)
        if (link.find('jpeg') > 0) and (link.find('https') < 0):
            img = link.split('base64,')[1]
            img = base64.b64decode(img)
            with open(save_dir + '/' + str(i) + '.jpg', 'wb') as f:
                f.write(img)
                f.close()
        elif (link.find('https') > 0):
            response = requests.get(link)
            img = Image.open(BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(save_dir + '/' + str(i) + '.jpg')
        else:
            continue

if __name__ == '__main__':
    links = _get_links('cat', search_engine='naver')
    _get_images_from_link(links)