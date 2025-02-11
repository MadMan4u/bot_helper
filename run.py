import subprocess

def check_for_updates():
    print("Проверка обновлений...")
    subprocess.run(["python", "config/update.py"])

def main():
    check_for_updates()  # Проверяем обновления перед выполнением команд

    print("Что вы хотите сделать?")
    print("1. Продублировать намерения NLU")
    print("2. Выгрузить речевые модули из робота")
    print("3. Загрузить в компанию статусы по шаблону робота (new.qsiq.ru)")
    print("4. Запустить конвертер")
    print("5. Удалить аудиозаписи в роботе")

    choice = input("Введите номер выбора: ")

    if choice == '1':
        # Запускаем файл parent_intents.py
        subprocess.run(["python", "config/nlu/parent_intents.py"])
    elif choice == '2':
        # Запускаем файл run.py
        subprocess.run(["python", "config/text_modules/run.py"])
    elif choice == '3':
        # Запускаем файл run.py
        subprocess.run(["python", "config/scenario/add_statuses.py"])
    elif choice == '4':
        # Запускаем файл run.py
        subprocess.run(["python", "config/converter.py"])
    elif choice == '5':
        # Запускаем файл run.py
        subprocess.run(["python", "config/reset_voices.py"])
    else:
        print("Неверный выбор.")

if __name__ == "__main__":
    main()
    input("Программа завершила работу")
