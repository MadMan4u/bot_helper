import requests
import json

def load_payload_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def authenticate(payload):
    url = "https://access.qsiq.ru/api/v1/user/login"
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred during authentication: {err}")
    except Exception as err:
        print(f"An error occurred during authentication: {err}")

def get_existing_statuses(campaign_id, token):
    url = f"https://campaigns.qsiq.ru/api/v2/statuses?campaign_id={campaign_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while fetching statuses: {err}")
    except Exception as err:
        print(f"An error occurred while fetching statuses: {err}")

def add_status(campaign_id, token, status_file):
    url = "https://campaigns.qsiq.ru/api/v2/statuses"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Загрузка шаблона payload
    payload = load_payload_from_file(status_file)
    
    # Обновление campaign_id в payload
    payload['campaign_id'] = int(campaign_id)  # Преобразование в int
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while adding status: {err}")
        print(f"Response content: {response.content.decode()}")  # Печать содержимого ответа
    except Exception as err:
        print(f"An error occurred while adding status: {err}")

# Пример использования
user_payload = load_payload_from_file('config/scenario/user.txt')  # Загрузка payload для аутентификации
auth_response = authenticate(user_payload)

if auth_response:
    token = auth_response.get("access_token")  # Получаем access_token
    if token:
        campaign_id = input("Введите ID компании: ")

        # Получение уже существующих статусов компании
        existing_statuses = get_existing_statuses(campaign_id, token)
        existing_names = {status["name"] for status in existing_statuses}  # Список уже существующих названий статусов
        
        # Список файлов со статусами
        status_files = [
            'scenario/statuses/Заявка.txt',
            'scenario/statuses/Без статуса АТМ.txt',
            'scenario/statuses/Брошена трубка.txt',
            'scenario/statuses/Отказ не нужно.txt',
            'scenario/statuses/Отказ негатив.txt',
            'scenario/statuses/Отказ нецелевой.txt',
            'scenario/statuses/Перезвон автоответчик.txt',
            'scenario/statuses/Перезвон не слышно.txt'
        ]

        # Добавляем каждый статус из списка, если его нет в существующих
        for status_file in status_files:
            payload = load_payload_from_file(status_file)  # Загружаем payload статуса
            status_name = payload.get("name")  # Получаем имя статуса из файла

            if status_name in existing_names:
                print(f"Статус '{status_name}' уже существует, пропускаем.")
            else:
                status_response = add_status(campaign_id, token, status_file)
                if status_response:
                    print(f"Статус '{status_name}' успешно добавлен:", status_response)
                else:
                    print(f"Не удалось добавить статус '{status_name}'.")
    else:
        print("Ошибка: не удалось получить access_token.")
else:
    print("Аутентификация не удалась.")
