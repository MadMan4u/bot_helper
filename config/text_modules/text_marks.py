import requests
import json
import sys
import os

# Добавляем путь к родительской директории, где находится auth.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import authorize
from table_creator import create_table  # Импортируем функцию создания таблицы для marks

# Создаем папку 'output', если она не существует
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Функция для фильтрации marker и introductionMessage из данных API
def get_filtered_data(data):
    result = []
    nodes = data.get("nodes", {})

    # Сначала собираем все introductionMessage и marker из nodes
    for node_id, node_data in nodes.items():
        properties = node_data.get("properties", {})
        introduction_message = properties.get("introductionMessage", [])
        marker = properties.get("marker", "")

        # Проверяем, если есть introductionMessage
        if introduction_message:
            # Фильтруем только строковые элементы из introduction_message
            filtered_introduction_message = [str(msg) for msg in introduction_message if isinstance(msg, str)]
            # Добавляем речевой модуль и marker в результат
            result.append({
                "introductionMessage": " ".join(filtered_introduction_message),
                "marker_text": marker  # Если marker отсутствует, оставляем пустым
            })

    return result

# Функция для сохранения отфильтрованных речевых модулей в txt файл
def save_filtered_modules(filtered_data, output_filename_txt):
    unique_phrases = []
    seen_phrases = set()

    # Собираем уникальные речевые модули и их markers
    for item in filtered_data:
        phrase = item['introductionMessage'].strip()
        marker_text = item['marker_text']  # Получаем текст marker
        if phrase not in seen_phrases:
            unique_phrases.append((phrase, marker_text))  # Сохраняем как кортеж (фраза, marker_text)
            seen_phrases.add(phrase)

    # Сохранение отфильтрованных речевых модулей в txt файл
    with open(os.path.join(output_dir, output_filename_txt), 'w', encoding='utf-8') as txt_file:
        for phrase, _ in unique_phrases:
            txt_file.write(f'{phrase}\n')

    return unique_phrases

# Получение токена
token = authorize('https://iam.twin24.ai/api/v1/auth/login', 'user.txt')

if token:
    bot_id = input("Введите ID бота: ")
    bot_url = f"https://bot.twin24.ai/api/v1/bots/{bot_id}"
    bot_headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }

    bot_response = requests.get(bot_url, headers=bot_headers)
    data = bot_response.json()

    # Фильтрация данных
    filtered_data = get_filtered_data(data)
    
    # Сохранение отфильтрованных речевых модулей в папку 'output'
    unique_phrases = save_filtered_modules(filtered_data, 'РМ_filtered.txt')

    # Создание таблицы с использованием markers и сохранение в папку 'output'
    create_table(unique_phrases, os.path.join(output_dir, 'table_marks.docx'))

else:
    print("Не удалось получить токен.")
