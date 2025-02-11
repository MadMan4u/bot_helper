import requests
import json
import sys
import os

# Добавляем путь к родительской директории, где находится auth.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import authorize
from table_creator import create_table  # Импортируем функцию создания таблицы для links

# Создаем папку 'output', если она не существует
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Функция для фильтрации links и introductionMessage из данных API
def get_filtered_data(data):
    result = []
    nodes = data.get("nodes", {})
    links = data.get("viewDetails", {}).get("generatedLabel", {}).get("links", {})

    # Сначала собираем все introductionMessage из nodes
    for node_id, node_data in nodes.items():
        properties = node_data.get("properties", {})
        introduction_message = properties.get("introductionMessage", [])

        # Преобразуем элементы introductionMessage в строки, если они не строки, и отбрасываем словари
        cleaned_messages = [
            str(msg) for msg in introduction_message if isinstance(msg, (str, int, float))
        ]

        # Проверяем, если есть очищенные introductionMessage
        if cleaned_messages:
            # Ищем соответствующие links для этого node_id
            link_text = None
            for link_id, intent_text in links.items():
                source_id, target_id = link_id.split('_')

                # Если target_id совпадает с node_id, то присваиваем links_text
                if target_id == node_id:
                    link_text = intent_text
                    break

            # Добавляем речевой модуль в результат
            result.append({
                "introductionMessage": " ".join(cleaned_messages),
                "links_text": link_text if link_text else ""  # Если link_text отсутствует, оставляем пустым
            })

    return result

# Функция для сохранения отфильтрованных речевых модулей в txt файл
def save_filtered_modules(filtered_data, output_filename_txt):
    unique_phrases = []
    seen_phrases = set()

    # Собираем уникальные речевые модули и их links
    for item in filtered_data:
        phrase = item['introductionMessage'].strip()
        links_text = item['links_text']  # Получаем текст links
        if phrase not in seen_phrases:
            unique_phrases.append((phrase, links_text))  # Сохраняем как кортеж (фраза, links_text)
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

    # Создание таблицы с использованием links и сохранение в папку 'output'
    create_table(unique_phrases, os.path.join(output_dir, 'table_links.docx'))

else:
    print("Не удалось получить токен.")
