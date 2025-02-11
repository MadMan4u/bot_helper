import json
import requests

# Загрузка email и пароля из файла user.txt
def load_credentials(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Функция авторизации, возвращающая токен
def authorize(url, credentials_file):
    # Загружаем email и пароль из файла
    credentials = load_credentials(credentials_file)

    # Загружаем данные для запроса
    payload = {
        "email": credentials["email"],
        "password": credentials["password"]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    # Отправка POST-запроса для авторизации
    response = requests.post(url, json=payload, headers=headers)

    # Проверка успешности авторизации
    if response.status_code == 200:
        # Возвращаем только токен
        return response.json()['token']
    else:
        raise Exception(f"Authorization failed: {response.text}")
