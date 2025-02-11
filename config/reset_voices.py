import json
import requests
import os

def clear_console():
    # Очистка консоли в зависимости от ОС
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bot_settings(bot_id, token):
    url = f"https://twin24.ai/cis/api/v1/botsSettings/{bot_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка в получение данных: {response.text}")

def update_bot_settings(payload, token):
    url = "https://twin24.ai/cis/api/v1/botsSettings"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка в обновлении данных: {response.text}")

def clear_records_in_nodes(nodes):
    """Очищает поле record в каждом узле nodes."""
    for node_id, node_data in nodes.items():
        if "records" in node_data and isinstance(node_data["records"], list):
            for record in node_data["records"]:
                record["record"] = ""  # Очищаем значение record
    return nodes

def main():
    try:
        # Подключаем модуль авторизации
        from auth import authorize

        # Авторизуемся и получаем токен
        credentials_file = "user.txt"
        auth_url = "https://iam.twin24.ai/api/v1/auth/login"
        token = authorize(auth_url, credentials_file)

        # Спрашиваем ID бота
        bot_id = input("Введите ID бота: ").strip()

        # Получаем настройки бота
        bot_settings = get_bot_settings(bot_id, token)

        # Извлекаем voiceId и nodes
        voice_id = bot_settings.get("voiceId")
        if not voice_id:
            raise Exception("voiceId не найден.")

        nodes = bot_settings.get("nodes")
        if not nodes:
            raise Exception("Узлы nodes не найдены в настройках.")

        # Очищаем записи в узлах
        cleared_nodes = clear_records_in_nodes(nodes)

        # Формируем payload для обновления настроек
        payload = {
            "id": bot_id,
            "botId": bot_id,
            "nodes": cleared_nodes,
            "voiceId": voice_id,
            "voiceTuner": {
                "temp": None,
                "pitch": None,
                "volume": None,
                "emotion": "neutral"
            },
            "globalVoiceActing": {
                "repeat": [],
                "redirect": [],
                "bigNumberContinue": []
            },
            "language": "RU",
            "speech": "AUDIO"
        }

        # Отправляем POST-запрос для обновления настроек
        update_response = update_bot_settings(payload, token)
        print("Настройки бота успешно обновлены:", update_response)

    except Exception as e:
        print("Произошла ошибка:", e)

if __name__ == "__main__":
    clear_console()
    print("Удаление аудиозаписей в роботе")
    main()
