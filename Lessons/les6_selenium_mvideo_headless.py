"""
* 2) Написать программу, которая собирает «Хиты продаж» с сайтов
техники mvideo, onlinetrade и складывает данные в БД. Магазины можно
выбрать свои. Главный критерий выбора: динамически загружаемые товары
"""

from time import sleep
import re
from selenium import webdriver  # Основной элемент
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient


def parse_site_with_selenium():
    options = Options()
    options.headless = True
    options.add_argument('window-size=1200x600')
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True
    driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)
    driver.get('https://www.mvideo.ru')
    sleep(2)
    products = []
    # Block "try" need for webdriver() permanently closed self process in OS system if there is any Exception.
    # This is a known unsolved issue:
    # https://github.com/webdriverio-boneyard/wdio-selenium-standalone-service/issues/28
    try:
        while True:
            bestseller_wrapper = driver.find_element_by_css_selector('.gallery-layout.sel-hits-block ')
            bestseller = bestseller_wrapper.find_elements_by_class_name('gallery-list-item')[:4]
            for item in bestseller:
                spam = item.find_element_by_class_name('sel-product-tile-title')
                title = spam.text
                url = spam.get_attribute('href')
                price = re.findall('[\\d]+\\.[\\d]{2}', spam.get_attribute('data-product-info'))[0]
                products.append({'title': title,
                                 'price': price,
                                 'url': url})
            button = bestseller_wrapper.find_element_by_css_selector('.next-btn.sel-hits-button-next')
            if button.get_attribute('class') != 'next-btn sel-hits-button-next disabled':
                button.click()
                sleep(2)
            else:
                break
        for prod in products:
            for key, value in prod.items():
                print(f'{key}: {value}')
            print()
    except Exception as e:
        print(e)
    driver.quit()
    return products


def client_mongo(db_name: str, collection_name: str):
    client = MongoClient('mongodb://127.0.0.1:27017')
    data_base = client[db_name]  # db name
    collect_name = data_base[collection_name]  # collection name
    return collect_name


def save_to_mongo(list_to_save_db: list, unique_key: str, db_name: str, collection_name: str):
    collection = client_mongo(db_name, collection_name)
    count = 0
    for item in list_to_save_db:
        spam = collection.find_one({unique_key: item[unique_key]})
        if spam is None:
            collection.insert_one(item)
            count += 1
    print(f'Added {count} records. Collection "{collection.name}" has {collection.count_documents({})} items.')


save_to_mongo(parse_site_with_selenium(), 'url', 'db_mvideo_bestseller', 'bestseller')
