import random
import requests
from bs4 import BeautifulSoup

def parse_proxy():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    response = requests.get('https://free-proxy-list.net/ru/', headers=headers, timeout=10)
    response.raise_for_status()
    
    # Парсим таблицу
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    
    proxy_list = []
    for row in table.tbody.find_all('tr'):
        columns = row.find_all('td')

        if ('Russian Federation' in columns[3].text):
            proxy_list.append(f'{columns[0].text.strip()}:{columns[1].text.strip()}')
    
    return proxy_list[random.randint(0, len(proxy_list) - 1)]