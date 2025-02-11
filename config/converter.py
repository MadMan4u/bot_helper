import os
import audioread
import wave
import numpy as np
from pydub import AudioSegment
from scipy.signal import resample

def clear_console():
    # Очистка консоли в зависимости от ОС
    os.system('cls' if os.name == 'nt' else 'clear')

def convert_mp3_to_wav(input_file, output_file):
    ''' Конвертация MP3 в WAV с частотой 8000 Гц и моно '''
    with audioread.audio_open(input_file) as audio_file:
        # Получаем параметры аудио
        sample_rate = audio_file.samplerate
        channels = audio_file.channels

        # Массив для хранения аудио данных
        audio_data = np.array([], dtype=np.int16)

        # Чтение буферов и добавление в общий массив
        for buffer in audio_file:
            buffer_data = np.frombuffer(buffer, dtype=np.int16)
            if channels > 1:
                buffer_data = buffer_data[::channels]  # Преобразуем в моно
            audio_data = np.concatenate((audio_data, buffer_data))

        # Ресемплирование аудио до 8000 Гц
        if sample_rate != 8000:
            audio_data = resample(audio_data, int(len(audio_data) * 8000 / sample_rate)).astype(np.int16)

        # Запись в WAV файл
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Моно
            wav_file.setsampwidth(2)  # 16 бит
            wav_file.setframerate(8000)  # Частота дискретизации 8000 Гц
            wav_file.writeframes(audio_data.tobytes())

def convert_all_mp3_in_folder(folder_path):
    ''' Конвертация всех MP3 файлов в папке в WAV '''
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3"):
            mp3_file = os.path.join(folder_path, filename)
            wav_file = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.wav")
            
            # Конвертируем MP3 в WAV
            convert_mp3_to_wav(mp3_file, wav_file)
            print(f"Конвертирован: {mp3_file} -> {wav_file}")
            
            # Удаляем исходный MP3 файл
            os.remove(mp3_file)
            print(f"Удалён: {mp3_file}")

def calculate_average_dBFS(folder_path):
    ''' Рассчитываем среднюю громкость всех файлов '''
    total_dBFS = 0
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".wav"):
            filepath = os.path.join(folder_path, filename)
            sound = AudioSegment.from_wav(filepath)
            total_dBFS += sound.dBFS
            count += 1
    return total_dBFS / count if count > 0 else -20  # По умолчанию -20 dBFS, если файлов нет

def normalize_audio(sound, target_dBFS):
    ''' Приведение громкости к целевому уровню dBFS '''
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def process_wav_files(folder_path):
    ''' Приведение всех файлов к одинаковой громкости и качеству '''
    average_dBFS = calculate_average_dBFS(folder_path)
    print(f"Средняя громкость всех файлов: {average_dBFS:.2f} dBFS")
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".wav"):
            filepath = os.path.join(folder_path, filename)
            
            # Открытие и преобразование аудио
            sound = AudioSegment.from_wav(filepath)
            
            # Если файл громче среднего уровня, понижаем громкость
            if sound.dBFS > average_dBFS:
                print(f"Обработка файла: {filename}, громкость {sound.dBFS:.2f} dBFS — будет понижена")
                normalized_sound = normalize_audio(sound, average_dBFS)
            else:
                print(f"Файл: {filename} уже на уровне или ниже среднего")
                normalized_sound = sound
            
            # Приведение к качеству 8000 Гц, 16 бит, моно
            normalized_sound = normalized_sound.set_frame_rate(8000).set_channels(1).set_sample_width(2)
            
            # Сохранение с новыми параметрами
            normalized_sound.export(filepath, format="wav")

def convert_and_process_audio(folder_path):
    ''' Основная функция: конвертация MP3 в WAV и обработка WAV файлов '''
    # 1. Конвертируем все MP3 файлы в WAV
    convert_all_mp3_in_folder(folder_path)
    
    # 2. Приводим все WAV файлы к одинаковой громкости и качеству
    process_wav_files(folder_path)

# Пример использования
folder_path = "audio"  # Замени на путь к папке с файлами
clear_console()
convert_and_process_audio(folder_path)
