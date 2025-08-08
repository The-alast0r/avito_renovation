import os
import random
import requests
import threading
import flet as ft
from loguru import logger
from avito_parser import *
from list_parser import parse_renovation_addresses

BEGIN_URL = 'https://www.avito.ru/moskva/kvartiry/prodam/vtorichka/pod-snos-ASgBAgICA0SSA8YQ5geMUvLCDujsmQI?context=&f=ASgBAgICBkSSA8YQ5geMUurBDf7OOfLCDujsmQKO3g4CkN4OAg&i=1&s=104'

def main(page: ft.Page):
    page.title = "Avito реновации"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_400

    # Парсинг настроек Telegram-бота
    telebot_settings = False
    if (os.path.exists('telebot.ini')):
        with open('telebot.ini', 'r') as f:
            settings_lines = f.read().splitlines()
        telebot_settings = {obj : state for obj, state in zip([x.split('=')[0] for x in settings_lines], [x.split('=')[1] for x in settings_lines])}
    
    # Элементы интерфейса
    private_proxy_username = ft.TextField(
        label="Юзер",
        hint_text="user",
        width=400
    )
    private_proxy_password = ft.TextField(
        label="Пароль",
        hint_text="password",
        width=400
    )
    private_proxy_host = ft.TextField(
        label="Хост",
        hint_text="proxy.example.com",
        width=400
    )
    private_proxy_port = ft.TextField(
        label="Порт",
        hint_text="8080",
        width=400
    )
    
    bot_token_field = ft.TextField(
        label="Telegram Bot Token",
        hint_text="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        value=telebot_settings['TOKEN'] if telebot_settings else '',
        width=400
    )
    
    chat_id_field = ft.TextField(
        label="Telegram Chat ID",
        hint_text="-1001234567890",
        value=telebot_settings['CHATID'] if telebot_settings else '',
        width=400
    )
    
    free_proxy_cb = ft.Checkbox(
        label="Использовать бесплатные прокси (не гарантируется стабильная работа)", 
        value=False,
        on_change=lambda e: logger.debug(f"[INFO] Использую бесплатные прокси")
    )
    
    debug_cb = ft.Checkbox(
        label="Debug Mode", 
        value=False,
        on_change=lambda e: logger.debug(f"[INFO] Запуск в DEBUG MODE")
    )
    
    # Создание кнопок
    start_btn = ft.ElevatedButton(
        "ЗАПУСК", 
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.GREEN
    )
    
    test_bot_btn = ft.ElevatedButton("Проверить бота")
    
    # Виджет для логов
    log_view = ft.ListView(expand=True, height=300)
    
    # Список элементов для блокировки/разблокировки
    ui_elements = [
        private_proxy_username,
        private_proxy_password,
        private_proxy_host,
        private_proxy_port,
        bot_token_field, 
        chat_id_field, 
        free_proxy_cb, 
        debug_cb,
        start_btn,
        test_bot_btn
    ]
    
    # Функция для добавления логов в интерфейс
    def log_to_ui(message):
        color = ft.Colors.GREEN_ACCENT
        if "ERROR" in message:
            color = ft.Colors.RED_400
        elif "WARNING" in message:
            color = ft.Colors.AMBER_400
        elif "INFO" in message:
            color = ft.Colors.CYAN_300
        elif "SUCCESS" in message:
            color = ft.Colors.GREEN_400
        
        log_view.controls.append(ft.Text(message, selectable=True, color=color, font_family="Consolas"))
        log_view.scroll_to(offset=-1, duration=100)
        page.update()
    
    # Настройка Loguru
    logger.remove()
    logger.add(lambda msg: log_to_ui(msg.strip()), format="{message}")

    # Функция для блокировки/разблокировки интерфейса
    def toggle_ui(enabled):
        for element in ui_elements:
            element.disabled = not enabled
        page.update()
    
    # Обработчики событий
    def start_parsing_click(e):
        use_private_proxy = True
        if (private_proxy_host.value == '' or private_proxy_port.value == ''):
            use_private_proxy = False
        else:
            name = private_proxy_username.value
            passw = private_proxy_password.value
            host = private_proxy_host.value
            port = private_proxy_port.value
            proxy = f'username={name}\npassword={passw}\nhost={host}\nport={port}'
            with open('proxy.ini', 'w+') as f:
                f.write(proxy)
        
        if (not os.path.exists('telebot.ini')):
            text = f'TOKEN={bot_token_field.value}\nCHATID={chat_id_field.value}'
            with open('telebot.ini', 'w+') as f:
                f.write(text)

        if (not os.path.exists('./renovation.db')):
            if (not parse_renovation_addresses()):
                logger.info("[ERROR] Завершаю работу из-за ошибки")
                return
        
        db_handler = DBHandler('renovation.db')
        data = db_handler.select_all_renovation_addresses()
        parser = AvitoParser(False, free_proxy_cb.value, data, debug_cb.value)

        while True:
            toggle_ui(False)  # Блокируем интерфейс
            logger.info("[INFO] Интерфейс заблокирован на время парсинга")

            threading.Thread(
                target=parser.start_parsing(BEGIN_URL, toggle_ui),
                daemon=True
            ).start()
            time.sleep(random.randint(180, 300))
    
    def test_bot_click(e):
        bot_token = bot_token_field.value
        chat_id = chat_id_field.value

        if (not os.path.exists('telebot.ini')):
            text = f'TOKEN={bot_token}\nCHATID={chat_id}'
            with open('telebot.ini', 'w+') as f:
                f.write(text)
        
        if not bot_token or not chat_id:
            logger.error("[ERROR] Введите токен и ID чата!")
            return
        
        logger.info("[INFO] Проверка Telegram бота...")
        
        def send_test_message():
            try:
                response = send_message(bot_token, chat_id, "Тестовое сообщение от парсера!")
                if response.status_code == 200:
                    logger.success("[SUCCESS] Бот работает! Сообщение отправлено.")
                else:
                    logger.error(f"[ERROR] Ошибка: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"[ERROR] Ошибка соединения: {str(e)}")
        
        threading.Thread(target=send_test_message, daemon=True).start()

    # Привязка обработчиков к кнопкам
    start_btn.on_click = start_parsing_click
    test_bot_btn.on_click = test_bot_click

    # Сборка интерфейса
    page.add(
        ft.Text("Настройки прокси:", weight=ft.FontWeight.BOLD),
        private_proxy_username,
        private_proxy_password,
        private_proxy_host,
        private_proxy_port,
        free_proxy_cb,
        
        ft.Divider(height=20),
        
        ft.Text("Настройки Telegram:", weight=ft.FontWeight.BOLD),
        bot_token_field,
        chat_id_field,
        test_bot_btn,
        
        ft.Divider(height=20),
        
        ft.Text("Дополнительные настройки:", weight=ft.FontWeight.BOLD),
        debug_cb,
        
        ft.Divider(height=20),
        
        start_btn,
        
        ft.Divider(height=20),
        
        ft.Text("Лог:", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=log_view,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=5,
            padding=10,
            bgcolor=ft.Colors.BLACK,
        )
    )

def send_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    return requests.get(url, params=params)

# Запуск приложения
if __name__ == "__main__":
    ft.app(target=main)