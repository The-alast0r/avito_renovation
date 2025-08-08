from address_prettifier import AddressPrettifier
from loguru import logger
import pandas as pd
import requests
import sqlite3
import tabula
import os
import re

def parse_renovation_addresses():
    table = pd.DataFrame()

    for file in os.listdir():
        if (re.search(r'Renovation[\s\S]*\.pdf', file)):
            table = tabula.read_pdf(file, pages='all')
            break

    if (table.empty):
        logger.info('[INFO] Не нашёл базу реновации в каталоге. Скачиваю с mos.ru...')
    
        try:
            response = requests.get("https://www.mos.ru/Renovation.pdf")
            response.raise_for_status()
            with open('Renovation.pdf', 'wb') as file:
                file.write(response.content)
            table = tabula.read_pdf('./Renovation.pdf', pages='all')
            
        except Exception:
            return False

    try:
        connect = sqlite3.connect('renovation.db')
        cursor = connect.cursor()
        prettifier = AddressPrettifier('mos.ru')
    
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS renovation (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            district TEXT NOT NULL,
            area TEXT NOT NULL,
            address TEXT NOT NULL
        )''')
        connect.commit()

        for row in table.iterrows():
            parts = row[1].tolist()
            if 'Округ' in parts[0]: continue
            prettifier.make_address_pretty(parts[2])
            cursor.execute('INSERT INTO renovation (district, area, address) VALUES (?, ?, ?)', (parts[0], parts[1], prettifier.pretty_address))

        connect.commit()
        connect.close()
    except Exception as e:
        return False