import time
import json
from loguru import logger
from driver_config import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

URL = 'https://www.avito.ru/moskva_i_mo/kvartiry/prodam?context=&s=104'

class AvitoParser:
    """Класс парсера Авито."""
    def __init__(self):
        self.session_apartments = []
        driver_config = DriverConfiguration()
        self.driver = webdriver.Firefox(options=driver_config.get_options(), service=driver_config.get_service())
        
        try:
            with open('seen.json', 'r') as file_seen:
                self.seen_apartments = set(json.load(file_seen))
        except FileNotFoundError:
            self.seen_apartments = set()

    def __get_url(self, url: str):
        self.driver.get(url)

        if 'Доступ ограничен' in self.driver.title:
            logger.debug('Доступ ограничен.\nДелаю паузу на 5 мин и пробую снова')
            time.sleep(300)
            self.__get_url(url)
        
    def __save_parsing_session(self):
        self.driver.quit()
        with open('seen.json', 'w+') as f:
            json.dump(list(self.seen_apartments), f)
        with open('temp.json', 'w+') as file:
            json.dump(self.session_apartments, file)

    def parse_avito(self, url):
        error_counter = 0
        page_n = 1
        
        while True:

            if (url is False):
                logger.success('Все объявления просмотрены!')
                break
            
            try:
                url = self.__parse_avito_page(url, page_n)
                logger.info('Пауза. Исключаю блокировку IP из-за частых запросов...')
                error_counter = 0
                page_n += 1
                time.sleep(5)
            except Exception as e:
                logger.debug('Ошибка. Работа будет продолжена через 20 секунд.\nЕсли ошибка повторится 3 раза подряд, программа завершится автоматически')
                error_counter += 1
                
                if (error_counter >= 3):
                    break
                time.sleep(20)
        
        self.__save_parsing_session()

    def __parse_avito_page(self, url, page_n):

        self.__get_url(url)

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
                # Парсинг данных
                title   = item.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text
                price   = item.find_element(By.CSS_SELECTOR, '[itemprop="price"]').get_attribute('content')
                address = item.find_element(By.CSS_SELECTOR, '[data-marker="item-address"]').text
                link    = item.find_element(By.CSS_SELECTOR, '[data-marker="item-title"]').get_attribute('href')

                # Проверка на повторный просмотр объявления
                id = item.get_attribute('data-item-id')
                if (id in self.seen_apartments):
                    break
                else:
                    self.seen_apartments.add(id)

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