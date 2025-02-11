import requests
import json
import sys
import os
import re

# Добавляем путь к родительской директории, где находится auth.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import authorize  # Импорт функции авторизации

def clear_console():
    # Очистка консоли в зависимости от ОС
    os.system('cls' if os.name == 'nt' else 'clear')

# Функция для получения списка намерений
def get_intents(nlu_id, token):
    # URL для получения намерений
    url = f"https://twin24.ai/nlu-backend/api/v1/agents/{nlu_id}/intents?page=0&limit=100&search=&sort=-createdAt"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }
    
    # Выполнение GET-запроса
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка получения намерений: {response.status_code}")
        return None

# Функция для извлечения нужных полей из намерений
def extract_intent_details(intents_data):
    items = intents_data.get("items", [])
    intents_details = []

    for item in items:
        intent_info = {
            "id": item.get("id"),
            "name": item.get("name"),
            "description": item.get("description"),
            "hexColor": item.get("hexColor")
        }
        intents_details.append(intent_info)

    return intents_details

# Функция для замены недопустимых символов на специальные последовательности
def replace_special_chars(filename):
    return filename.replace("/", "_slash_").replace("?", "_question_")

# Функция для восстановления оригинальных символов из специальных последовательностей
def restore_special_chars(filename):
    return filename.replace("_slash_", "/").replace("_question_", "?")

# Функция для экспорта фраз из намерений
def export_phrases(intent_id, token, intent_name):
    # Заменяем недопустимые символы для имени файла
    clean_intent_name = replace_special_chars(intent_name)
    
    # URL для экспорта фраз
    url = f"https://twin24.ai/nlu-backend/api/v1/intents/{intent_id}/phrases/export"
    
    payload = {
        "format": "txt"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    # Отправка POST-запроса для экспорта фраз
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Создаем папку output/phrases_nlu, если она не существует
        os.makedirs("output/phrases_nlu", exist_ok=True)
        
        # Запись фраз в файл в папке output/phrases_nlu
        file_path = os.path.join("output/phrases_nlu", f"{clean_intent_name}.txt")
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(response.text)  # Сохраняем текст в файл
        print(f"Фразы из намерения '{intent_name}' экспортированы в файл '{file_path}'")
        return file_path  # Возвращаем путь к файлу для дальнейшего использования
    else:
        print(f"Ошибка экспорта фраз для намерения '{intent_name}': {response.status_code}")
        return None

# Функция для загрузки намерений из родительского NLU в детский
def upload_intents_to_child(child_nlu_id, intents, token):
    url = f"https://twin24.ai/nlu-backend/api/v1/agents/{child_nlu_id}/intents"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    
    intent_files = {}  # Словарь для хранения файлов с фразами

    for intent in intents:
        # Экспортируем фразы из родительского намерения
        file_path = export_phrases(intent['id'], token, intent['name'])
        if file_path:
            intent_files[intent['id']] = file_path  # Сохраняем путь к файлу

        # Загружаем намерение в детский NLU
        payload = {
            "name": intent['name'],
            "description": intent['description'],
            "hexColor": intent['hexColor']
        }
        
        # Отправка POST-запроса для загрузки намерения в детский NLU
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"Намерение '{intent['name']}' успешно загружено в детский NLU.")
            # Импортируем фразы в загруженное намерение
            child_intent_id = response.json()['id']
            import_phrases(child_intent_id, token, intent['name'])
        else:
            print(f"Ошибка загрузки намерения '{intent['name']}': {response.status_code} - {response.text}")

# Функция для импорта фраз в намерение
def import_phrases(intent_id, token, intent_name):
    # Заменяем недопустимые символы для имени файла
    clean_intent_name = replace_special_chars(intent_name)
    
    # URL для импорта фраз
    url = f"https://twin24.ai/nlu-backend/api/v1/intents/{intent_id}/phrases/import"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }
    
    # Путь к файлу с фразами
    file_path = os.path.join("output/phrases_nlu", f"{clean_intent_name}.txt")
    
    # Проверка существования файла
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            files = {'file': (f"{clean_intent_name}.txt", file, 'text/plain')}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            # Восстанавливаем оригинальное имя намерения для вывода
            original_intent_name = restore_special_chars(intent_name)
            print(f"Фразы из файла '{clean_intent_name}.txt' успешно импортированы в намерение '{original_intent_name}'.")
        else:
            print(f"Ошибка импорта фраз в намерение '{intent_name}': {response.status_code} - {response.text}")
    else:
        print(f"Файл '{clean_intent_name}.txt' не найден.")

# Основной блок программы
if __name__ == "__main__":
    clear_console()
    print('Дублирование намерений NLU')
    # Запрашиваем у пользователя ID родительского NLU
    parent_nlu_id = input("Введите ID родительского NLU: ")
    # Запрашиваем у пользователя ID для импорта NLU
    child_nlu_id = input("Введите ID для импорта NLU: ")

    # Получаем токен с помощью функции авторизации из auth.py
    token = authorize("https://iam.twin24.ai/api/v1/auth/login", 'user.txt')

    if token:
        # Получаем намерения из родительского NLU
        intents = get_intents(parent_nlu_id, token)

        if intents:
            # Извлекаем нужные поля (id, name, description, hexColor)
            intents_details = extract_intent_details(intents)

            # Дублируем намерения в детском NLU и экспортируем фразы
            upload_intents_to_child(child_nlu_id, intents_details, token)
    else:
        print("Не удалось получить токен")
