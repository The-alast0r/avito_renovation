from loguru import logger
import sqlite3
import tabula
import os
import re

def parse_renovation_addresses():
    tables = False
    try:
        logger.info('Скачиваю базу с сайта mos.ru...')
        tables = tabula.read_pdf("https://www.mos.ru/Renovation.pdf", pages='all')
    except Exception:
        logger.info('Отсутствует связь с интернетом. Ищу файл Renovation.pdf в каталоге...')

    if (not tables):
        for file in os.listdir():
            if (re.search(r'Renovation[\s\S]*\.pdf', file)):
                tables = tabula.read_pdf(file, pages='all')
                break

    if (not tables):
        logger.error('Ошибка: отсутствует база реновации с сайта mos.ru')
        return

    try:
        connect = sqlite3.connect('workbase.db')
        cursor = connect.cursor()
    
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS renovation (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            district TEXT NOT NULL,
            area TEXT NOT NULL,
            address TEXT NOT NULL
        )''')
        connect.commit()

        for table in tables:
            for idx, row in table.iterrows():
                cursor.execute('INSERT INTO renovation (district, area, address) VALUES (?, ?, ?)', (row['Округ'], row['Район'], row['Улица']))

        connect.commit()
        connect.close()
    except Exception:
        logger.error('Ошибка при работе с базой данных')
        return