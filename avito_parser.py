import time
import json
from loguru import logger
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class AvitoParser:
    def __init__(self):
        self.session_apartments = []
        self.use_proxy          = False

        try:
            with open('proxy.ini', 'r') as file_proxy:
                settings_lines = file_proxy.read().splitlines()
            proxy_settings = {obj : state for obj, state in zip([x.split('=')[0] for x in settings_lines], [x.split('=')[1] for x in settings_lines])}

            if (proxy_settings['username'] == '' or proxy_settings['password'] == '' or proxy_settings['host'] == '' or proxy_settings['port'] == ''):
                logger.debug('Не обнаружил прокси. Работаю без использования прокси-сервера')
            else:
                proxy_string = f'{proxy_settings['username']}:{proxy_settings['password']}@{proxy_settings['host']}:{proxy_settings['port']}'
                self.proxy   = proxy_string
                logger.info(f'Использую прокси: {proxy_string}')
                self.use_proxy = True
                
        except FileNotFoundError:
            logger.error('Отсутствует файл конфигурации прокси!')
            return

        try:
            with open('seen.json', 'r') as file_seen:
                self.seen_apartments = set(json.load(file_seen))
        except FileNotFoundError:
            self.seen_apartments = set()

    def __get_url(self, url: str):
        self.driver.get(url)
        
    def __save_session(self):
        self.driver.quit()
        with open('seen.json', 'w+') as f:
            json.dump(list(self.seen_apartments), f)
        with open('temp.json', 'w+') as file:
            json.dump(self.session_apartments, file)

    def start_parsing(self, begin_url):
        page_n = 1
        url = begin_url
        error_counter = 0

        with SB(uc=True,
                headless=False,
                browser='chrome',
                proxy=self.proxy if self.use_proxy else None
            ) as self.driver:

            while True:

                if (url is False):
                    logger.success('Все объявления просмотрены!')
                    break

                try:
                    url = self.__parse_page(url, page_n)
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
                    
            self.__save_session()
        

    def __parse_page(self, url, page_n):

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