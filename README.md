# 🔍 Avito Реновации - проверка жилья в программе реновации Москвы

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue)](https://t.me/junior_lair)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Инструмент для автоматического поиска объявлений на Avito о продаже квартир, попадающих под программу реновации Москвы.**   
Приложение сравнивает адреса из объявлений с официальным списком домов на реновацию с mos.ru и мгновенно уведомляет вас через Telegram-бота.

## 🚀 Основные возможности

- **Автоматический парсинг** объявлений с Avito в реальном времени
- **Сравнение адресов** с официальной базой домов реновации Москвы
- **Мгновенные уведомления** в Telegram о новых подходящих объявлениях
- **Гибкая система прокси**:
  - Использование собственных прокси-серверов
  - Автопарсинг бесплатных прокси с различных источников

## ⚙️ Установка и настройка

### Требования
- Python 3.8+
- Telegram аккаунт (для получения уведомлений)

### Установка
```bash
# Клонирование репозитория
git clone https://github.com/ваш-пользователь/avito-renovation.git
cd avito-renovation

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python ./app.py
```

### Настройка Telegram-бота
1. Создайте бота в @BotFather
2. Получите token бота и id чата с ним

### Поблагодарить автора
[telegram-канал](https://t.me/junior_lair)