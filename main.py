from list_parser import parse_renovation_addresses
from avito_parser import *

BEGIN_URL = 'https://www.avito.ru/moskva_i_mo/kvartiry/prodam?context=&s=104'

if __name__ == '__main__':

    parser = AvitoParser()
    parsed_apartments = []
    error_counter = 0
    page_n = 1
    url = BEGIN_URL
    
    while True:
        
        if (error_counter >= 3):
            break

        if (url is False):
            logger.success('Все объявления просмотрены!')
            break
        
        try:
            parser.get_url(url)
            url = parser.parse_page(page_n)
            logger.info('Пауза. Исключаю блокировку IP из-за частых запросов...')
            error_counter = 0
            page_n += 1
            time.sleep(5)
        except Exception as e:
            logger.debug(e)
            # logger.debug('Ошибка. Работа будет продолжена через 20 секунд.\nЕсли ошибка повторится 3 раза подряд, программа завершится автоматически')
            error_counter += 1
            time.sleep(20)
    
    parser.save_session()