import os
import requests

class BotAlarmer:
    """Отправляет сообщение при помощи бота, если находится объявление."""
    def __init__(self):
        if (os.path.exists('telebot.ini')):
            with open('telebot.ini', 'r') as f:
                settings_lines = f.read().splitlines()
            telebot_settings = {obj : state for obj, state in zip([x.split('=')[0] for x in settings_lines], [x.split('=')[1] for x in settings_lines])}
        self.token = telebot_settings['TOKEN']
        self.chat_id = telebot_settings['CHATID']
    
    def send_message(self, address, link):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        params = {
            "chat_id": self.chat_id,
            "text": f"""🏘️ Новое объявление!\n\n📍 Адрес: {address}\n🔗 Ссылка:\n{link}\n\n"""
        }
        return requests.get(url, params=params)