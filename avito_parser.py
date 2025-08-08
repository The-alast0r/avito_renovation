import time
import json
from dbhandler import *
import free_proxy_parser
from loguru import logger
from seleniumbase import Driver
from bot_alarmer import BotAlarmer
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from address_prettifier import AddressPrettifier
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AvitoParser:
    def __init__(self, private_proxy, free_proxy, renovation_data, debug_mode=False):
        self.session_apartments = []
        self.private_proxy      = private_proxy
        self.free_proxy         = free_proxy
        self.debug_mode         = debug_mode
        self.renovation_data    = renovation_data

        if (self.private_proxy and not free_proxy):
            try:
                with open('proxy.ini', 'r') as file_proxy:
                    settings_lines = file_proxy.read().splitlines()
                proxy_settings = {obj : state for obj, state in zip([x.split('=')[0] for x in settings_lines], [x.split('=')[1] for x in settings_lines])}

                if (proxy_settings['username'] == '' or proxy_settings['password'] == '' or proxy_settings['host'] == '' or proxy_settings['port'] == ''):
                    logger.debug('[WARNING] Не обнаружил прокси. Работаю без использования прокси-сервера')
                else:
                    proxy_string = f'{proxy_settings['username']}:{proxy_settings['password']}@{proxy_settings['host']}:{proxy_settings['port']}'
                    self.proxy   = proxy_string
                    logger.info(f'[INFO] Использую прокси: {proxy_string}')
                    
            except FileNotFoundError:
                logger.debug('[WARNING] Отсутствует файл конфигурации прокси!\nРаботаю без использования прокси-сервера...')

        elif (self.free_proxy):
            self.proxy = free_proxy_parser.parse_proxy()

        else:
            logger.debug('[WARNING] Работаю без прокси. Есть риск блокировки IP!')

        try:
            with open('seen.json', 'r') as file_seen:
                self.seen_apartments = set(json.load(file_seen))
        except FileNotFoundError:
            self.seen_apartments = set()

        self.driver = Driver(uc=True,
                            headless2=False if self.debug_mode else True,
                            browser='chrome',
                            proxy=self.proxy if self.private_proxy or self.free_proxy else None,
                            agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')

    def __get_url(self, url: str):
        self.driver.get(url)
        attempt = 0

        while 'Доступ ограничен' in self.driver.get_title():
            logger.debug('[WARNING] Avito заблокировал IP. Рекомендую сменить прокси, либо зайти в DEBUG MODE и пройти капчу')
            attempt+=1
            
            if (attempt >= 3):
                logger.error('[ERROR] Завершаю работу из-за блокировки IP')
                return False

            time.sleep(15)

        return True

    def __save_session(self):
        with open('seen.json', 'w+') as f:
            json.dump(list(self.seen_apartments), f)

        db_handler = DBHandler('parsed.db')
        db_handler.save_parsed_apartments(self.session_apartments)

    def start_parsing(self, begin_url, callback):
        self.stop_parsing = False
        page_n = 1
        url = begin_url
        prettifier = AddressPrettifier('avito')
        alarmer    = BotAlarmer()

        while True:

            if (self.stop_parsing or url is False):
                logger.success('[SUCCESS] Все объявления просмотрены!')
                break

            url = self.__parse_page(url, page_n, prettifier, alarmer)
            logger.info('[INFO] Пауза. Исключаю блокировку IP из-за частых запросов...')
            page_n += 1
            time.sleep(5)
                    
        self.__save_session()

        callback(True)

    def __parse_page(self, url, page_n, prettifier, alarmer):

        if (not self.__get_url(url)):
            return False

        logger.info(f"Обработка страницы {page_n}...")
        
        # Ожидание загрузки контента
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item"]')))
        except TimeoutException as error:
            logger.error(f"[ERROR] Не удалось соединиться с сайтом avito!\n{error}")
            
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
                    self.stop_parsing = True
                    break
                else:
                    self.seen_apartments.add(id)

                prettifier.make_address_pretty(address)
                if (prettifier.pretty_address in self.renovation_data):
                    alarmer.send_message(prettifier.pretty_address, link)             
                self.session_apartments.append({
                    'title': title,
                    'price': price,
                    'address': prettifier.pretty_address,
                    'link': link
                })
            except Exception as e:
                logger.debug('[WARNING] Ошибка при парсинге объявления. Возможно парсер схавал предложку. Работа будет продолжена')
                continue
        
        try:
            next_page_button = self.driver.find_element(By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]')
            return next_page_button.get_attribute('href')
        except Exception as e:
            return False