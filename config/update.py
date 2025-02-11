import os
import time
import requests
import zipfile
import shutil

# URL на GitHub с файлом version.txt
VERSION_URL = "https://raw.githubusercontent.com/MadMan4u/bot_helper/main/config/version.txt"
# URL для скачивания архива с обновлением
ZIP_URL = "https://github.com/MadMan4u/bot_helper/releases/latest/download/update.zip"
LOCAL_VERSION_FILE = "config/version.txt"

def get_remote_version():
    try:
        response = requests.get(VERSION_URL)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return None

def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as file:
            return file.read().strip()
    return "0"

def download_update():
    zip_path = "update.zip"
    try:
        response = requests.get(ZIP_URL, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return zip_path
    except requests.RequestException:
        return None

def install_update(zip_path):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("update_temp")
    
    for root, _, files in os.walk("update_temp"):
        for file in files:
            src = os.path.join(root, file)
            dst = src.replace("update_temp" + os.sep, "")
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)
    
    shutil.rmtree("update_temp")
    os.remove(zip_path)

def restart_app():
    time.sleep(2)  # Даем файлам замениться
    os.system("start run.exe")  # Запускаем заново (Windows)

def main():
    remote_version = get_remote_version()
    local_version = get_local_version()

    if remote_version and remote_version != local_version:
        print("Доступно обновление! Загружаем...")
        zip_path = download_update()
        if zip_path:
            print("Обновление загружено. Устанавливаем...")
            install_update(zip_path)
            print("Обновление установлено. Перезапуск...")
            restart_app()
        else:
            print("Ошибка загрузки обновления.")
    else:
        print("Обновлений нет.")

if __name__ == "__main__":
    main()
