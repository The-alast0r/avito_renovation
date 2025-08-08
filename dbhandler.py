import sqlite3

class DBHandler:
    """Класс для взаимодействия с основными базами данных."""
    def __init__(self, db_name):
        self.db_name = db_name
        
    def select_all(self):
        self.__connect()
        self.cursor.execute('SELECT * FROM renovation')
        result = self.cursor.fetchall()
        self.__disconnect()
        return result

    def select_all_renovation_addresses(self):
        if ('renovation.db' not in self.db_name):
            return False
        self.__connect()
        self.cursor.execute('SELECT address FROM renovation')
        result = [x[0] for x in self.cursor.fetchall()]
        self.__disconnect()
        return result

    def save_parsed_apartments(self, parsed):
        if ('parsed.db' not in self.db_name):
            return False
        self.__connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS renovation (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            title TEXT NOT NULL,
            price TEXT NOT NULL,
            address TEXT NOT NULL,
            link TEXT NOT NULL
        )''')
        self.__commit()

        for item in parsed:
            self.cursor.execute('INSERT INTO renovation (title, price, address, link) VALUES (?, ?, ?, ?)', (item['title'], item['price'], item['address'], item['link']))
        self.__commit()
        self.__disconnect()

    def __connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def __commit(self):
        self.connection.commit()
        
    def __disconnect(self):
        self.connection.close()
        