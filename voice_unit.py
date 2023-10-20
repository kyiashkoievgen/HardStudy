import pyaudio
import wave
import webrtcvad
import pygame
import librosa
from fastdtw import fastdtw
import numpy as np
import pocketsphinx
import os
import pyttsx3
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

from google.cloud import speech
import io
from db import DB


def speek_recognaizer_google():
    # Создайте клиент для API
    client = speech.SpeechClient()

    # Откройте аудиофайл
    with io.open("2.wav", "rb") as audio_file:
        content = audio_file.read()

    # Создайте объект аудио
    audio = speech.RecognitionAudio(content=content)

    # Укажите конфигурацию запроса (например, язык и формат аудио)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="pt-br",
    )

    # Отправьте запрос на распознавание
    response = client.recognize(config=config, audio=audio)

    # Выведите распознанный текст
    for result in response.results:
        print("Распознанный текст: {}".format(result.alternatives[0].transcript))


def speek_recognaizer_offline():
    # Путь к моделям и словарям
    model_path = r"C:\Users\User\Documents\project\HardStudy\cmusphinx_model\cmusphinx-pt-br-5.2"
    dict_path = r"C:\Users\User\Documents\project\HardStudy\cmusphinx_model\br-pt.dic"
    # model_path = r"C:\Users\User\Documents\project\HardStudy\cmusphinx_model\cmusphinx-ru-5.2"
    # dict_path = r"C:\Users\User\Documents\project\HardStudy\cmusphinx_model\cmusphinx-ru-5.2\ru.dic"
    audio_file_path = "1.wav"

    # Инициализация распознавателя
    config = pocketsphinx.Decoder.default_config()
    config.set_string("-hmm", model_path)
    # config.set_string("-lm", os.path.join(model_path, "ru.lm"))
    config.set_string("-dict", dict_path)

    decoder = pocketsphinx.Decoder(config)

    # Открываем аудиофайл
    stream = open(audio_file_path, "rb")

    # Декодируем аудиофайл
    decoder.start_utt()
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
    decoder.end_utt()

    # Получаем результат распознавания
    recognized_text = decoder.hyp().hypstr
    print("Распознанный текст:", recognized_text)


def convert_mp3_to_wav(audio_file_mp3, audio_file_wav):
    # Загрузка аудиофайла
    audio = AudioSegment.from_mp3(audio_file_mp3)

    # Сохранение в формате WAV
    audio.export(audio_file_wav, format="wav")

    print("Файл конвертирован в WAV:", audio_file_wav)


def play_sound(audio_file):
    # Инициализация Pygame
    pygame.init()

    # Создание объекта для воспроизведения звука
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)

    # Воспроизведение аудиофайла
    pygame.mixer.music.play()

    # Ожидание завершения воспроизведения (или другой логики)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Завершение Pygame
    pygame.quit()


def dtf(audio_file1, audio_file2):
    # Загрузка аудиоданных с использованием librosa
    y1, sr1 = librosa.load(audio_file1)
    y2, sr2 = librosa.load(audio_file2)

    # Извлечение характеристик MFCC (Mel-frequency cepstral coefficients)
    mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1)
    mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2)

    # Вычисление DTW между двумя наборами MFCC
    distance, path = fastdtw(mfcc1.T, mfcc2.T)

    # Вывод результата
    print("Расстояние DTW между аудиофайлами:", distance)

    # Путь выравнивания
    print("Путь выравнивания DTW:", path)


def mic_record():
    # Параметры записи
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Рекомендуется использовать 16кГц для VAD
    RECORD_SECONDS = 20
    buf_length = 30  # Длина буфера (в миллисекундах)
    OUTPUT_FILENAME = "recorded_audio.wav"
    # Инициализация PyAudio и VAD
    audio = pyaudio.PyAudio()
    vad = webrtcvad.Vad()

    # Устанавливаем уровень чувствительности VAD (1 - 3, где 3 - самый чувствительный)
    vad.set_mode(3)

    # Начало записи
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=480)
    print("Запись...")

    frames = []

    while True:
        data = stream.read(480)

        # Проверяем, активна ли голосовая активность
        if vad.is_speech(data, RATE):
            frames.append(data)
            print("Голосовая активность обнаружена.")

        # Останавливаем запись, если голосовая активность прекратилась
        elif len(frames) > 0:
            print("Голосовая активность завершена.")
            break

    # Остановка записи
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Сохранение записи в файл
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print("Аудио записано в файл:", OUTPUT_FILENAME)


def speak(text, rate=150, volume=1.0, voice='pt-br'):
    engine = pyttsx3.init()

    # Установите желаемый язык для генерации речи (португальский)
    engine.setProperty('rate', rate)  # Настройте скорость произношения (опционально)
    engine.setProperty('volume', 1.0)  # Настройте громкость (опционально)
    engine.setProperty('voice', voice)  # Установите голос на португальский (Бразилия)
    engine.say(text)
    engine.runAndWait()


def mp4_to_wav(video_file, audio_output_file, desired_sample_rate=16000, desired_channels=1):
    video_clip = VideoFileClip(video_file)
    audio = video_clip.audio
    # Сохраните измененную аудиодорожку
    audio.write_audiofile(audio_output_file)
    # Загрузите аудиодорожку
    audio = AudioSegment.from_file(audio_output_file)

    audio = audio.set_frame_rate(desired_sample_rate)
    audio = audio.set_channels(desired_channels)
    # Сохраните измененную аудиодорожку
    audio.export(audio_output_file, format='wav')


from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def split_video(cur_les):
    db = DB()
    db.del_null_row(cur_les)
    video_data = db.get_video_study_data(cur_les)
    print(video_data)
    input_video = db.get_video_file_name(video_data[0]['video_id'])
    print(input_video)
    for item in video_data:
        start_time = float(item['start_time'])
        end_time = float(item['stop_time'])

        output_video = f'video\\split_file\\{item["id"]}{item["video_id"]}.mp4'
        ffmpeg_extract_subclip(input_video, start_time, end_time, targetname=output_video)


#
# # Воспроизводим вырезанный отрезок видео
# from moviepy.editor import VideoFileClip
# clip = VideoFileClip(output_video)
# clip.preview()

import speech_recognition as sr
import os
from googletrans import Translator

# Создайте объект Recognizer
recognizer = sr.Recognizer()


# Укажите путь к аудиофайлу в формате WAV
# audio_file = "D:\\FFOutput\\chunk-01.wav"

# Откройте аудиофайл и распознайте его


# Укажите путь к каталогу, который вы хотите просканировать
# directory_path = 'D:\FFOutput\chunk'

def audio_file_recognizer(file_path, lang):
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)  # Запись аудио из файла
        try:
            text = recognizer.recognize_google(audio,
                                               language=lang)  # Распознавание с использованием Google Speech Recognition
            return text

        except sr.UnknownValueError:
            print("Речь не распознана")
            return ''
        except sr.RequestError as e:
            print(f"Ошибка запроса к сервису Google Speech Recognition; {e}")
            return ''


def audio_files_recognizer(directory_path):
    # Переберите все файлы в указанном каталоге
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Выведите полный путь к каждому файлу
            audio_file = os.path.join(root, file)
            print(audio_file)
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)  # Запись аудио из файла
                try:
                    text = recognizer.recognize_google(audio,
                                                       language="en-US")  # Распознавание с использованием Google Speech Recognition
                    print("Распознанный текст:", text)
                    with open(f"{audio_file}_eng.txt", "w", encoding="utf-8") as output_file:
                        output_file.write(text)
                except sr.UnknownValueError:
                    print("Речь не распознана")
                except sr.RequestError as e:
                    print(f"Ошибка запроса к сервису Google Speech Recognition; {e}")


def file_translator(directory_path):
    # Создайте объект Translator
    translator = Translator()
    # Переберите все файлы в указанном каталоге
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Проверьте, что файл имеет расширение .txt (или другое, если вам нужны другие форматы)
            if file.endswith(".txt"):
                # Выведите полный путь к найденному текстовому файлу
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()

                # Переведите текст с английского на русский
                translated_text = translator.translate(text, src="en", dest="ru")

                output_file = f"{file_path}_ru.txt"
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(translated_text.text)


# from moviepy.editor import VideoFileClip
#
# if __name__ == '__main__':
#     clip = VideoFileClip('C:\\Users\\User\\Documents\\project\\HardStudy\\video\\3 Perplexing Physics Problems.mp4')
#     cl = clip.set_start((5, 30))
#     cl.
