"""
1) Написать программу, которая собирает входящие письма из своего
или тестового почтового ящика и сложить данные о письмах в базу
данных (от кого, дата отправки, тема письма, текст письма)

* 2) Написать программу, которая собирает «Хиты продаж» с сайтов
техники mvideo, onlinetrade и складывает данные в БД. Магазины можно
выбрать свои. Главный критерий выбора: динамически загружаемые товары
"""

import time
from selenium import webdriver  # Основной элемент
from selenium.webdriver.common.keys import Keys  # Клавиши клавиатуры
from pymongo import MongoClient


def parse_site_with_selenium():
    driver = webdriver.Chrome()
    driver.get('https://mail.ru')

    elem = driver.find_element_by_id('mailbox:login')
    elem.send_keys('test-bender@mail.ru')
    elem = driver.find_element_by_id('mailbox:password')
    elem.send_keys('youpieceofmeat')
    elem.send_keys(Keys.RETURN)

    time.sleep(8)  # Download page maybe so long

    letters_class_name = 'llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal'
    len_letters = len(driver.find_elements_by_xpath(f'//a[contains(@class, "{letters_class_name}")]'))
    # print(len_letters)
    letters_all = []

    for i in range(len_letters):
        letters = driver.find_elements_by_xpath(f'//a[contains(@class, "{letters_class_name}")]')
        # print(letters[i].get_attribute('href'))
        letters[i].click()
        time.sleep(3)

        letter_author = driver.find_element_by_class_name('letter__contact-item').text
        letter_date = driver.find_element_by_class_name('letter__date').text
        letter_topic = driver.find_element_by_class_name('thread__subject').text
        letter_content = driver.find_element_by_class_name('letter-body').text

        # print(letter_author, letter_date, letter_topic)
        # print(letter_text, '\n')
        letters_all.append({'author': letter_author,
                            'date': letter_date,
                            'topic': letter_topic,
                            'content': letter_content})

        driver.get('https://e.mail.ru/inbox/')
        time.sleep(3)

    driver.quit()
    return letters_all


def client_mongo():
    client = MongoClient('mongodb://127.0.0.1:27017')
    data_base = client['db_mail_letters']  # db name
    mail_letters = data_base.mail_letters  # collection name
    return mail_letters


def save_to_mongo(letters: list):
    mail_letters = client_mongo()
    count = 0
    for letter in letters:
        spam = mail_letters.find_one({'content': letter['content']})
        if spam is None:
            mail_letters.insert_one(letter)
            count += 1
    print(f'Added {count} records. Collection "{mail_letters.name}" has {mail_letters.count_documents({})} letters')


save_to_mongo(parse_site_with_selenium())
