import subprocess
import os

def clear_console():
    # Очистка консоли в зависимости от ОС
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
        clear_console()
        print("Как осуществить выгрузку?")
        print("1. Через маркеры")
        print("2. Через стрелки")

        choice = input("Введите номер выбора: ")

        if choice == '1':
            subprocess.run(["python", "config/text_modules/text_marks.py"])
        elif choice == '2':
            subprocess.run(["python", "config/text_modules/text_links.py"])
        else:
            print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")

if __name__ == "__main__":
    main()
