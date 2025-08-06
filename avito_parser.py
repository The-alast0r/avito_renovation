from loguru import logger
from driver_config import *
import time
import json
import re
import os

URL = 'https://www.avito.ru/moskva_i_mo/kvartiry/prodam?context=&s=104'

class AvitoParser:
    def __init__(self):
        self.session_apartments = []
        driver_config = DriverConfiguration()
        self.driver = webdriver.Firefox(options=driver_config.get_options(), 
                                        service=driver_config.get_service()
                                        )
        
        try:
            with open('seen.json', 'r') as file_seen:
                self.seen_apartments = set(json.load(file_seen))
        except FileNotFoundError:
            self.seen_apartments = set()

    def get_url(self, url: str):
        self.driver.get(url)

        if 'Доступ ограничен' in self.driver.title:
            logger.error('Доступ ограничен. Нужен прокси')
        else:
            # logger.info('Доступ разрешён')
            pass

    def save_session(self):
        self.driver.quit()
        with open('seen.json', 'w+') as f:
            json.dump(list(self.seen_apartments), f)
        with open('temp.json', 'w+') as file:
            json.dump(self.session_apartments, file)


    def parse_page(self, page_n):

        logger.info(f"Обработка страницы {page_n}...")
        
        # Ожидание загрузки контента
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item"]')))
        except TimeoutException as error:
            logger.error(f"Не удалось соединиться с сайтом avito!\n{error}")
            
        # Прокрутка для загрузки всех элементов
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Поиск всех объявлений
        items = self.driver.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
        
        for item in items:
            try:
                # Проверка на повторный просмотр объявления
                id = item.get_attribute('data-item-id')
                if (id in self.seen_apartments):
                    break
                else:
                    self.seen_apartments.add(id)

                # Парсинг данных
                title   = item.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text
                price   = item.find_element(By.CSS_SELECTOR, '[itemprop="price"]').get_attribute('content')
                address = item.find_element(By.CSS_SELECTOR, '[data-marker="item-address"]').text
                link    = item.find_element(By.CSS_SELECTOR, '[data-marker="item-title"]').get_attribute('href')

                self.session_apartments.append({
                    'title': title,
                    'price': price,
                    'address': address,
                    'link': link
                })
            except Exception as e:
                logger.debug('Ошибка при парсинге объявления. Возможно парсер схавал предложку\nРабота будет продолжена')
                continue
        
        try:
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]')
            return next_page_button.get_attribute('href')
        except NoSuchElementException as e:
            return False