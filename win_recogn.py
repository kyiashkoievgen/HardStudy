import speech_recognition as sr

recognizer = sr.Recognizer()

# Установите движок распознавания речи на Windows Speech Platform
recognizer.recognize_sphinx = None  # Отключите другие движки
recognizer.recognize_google = None
recognizer.recognize_wit = None
recognizer.recognize_bing = None
recognizer.recognize_houndify = None
recognizer.recognize_ibm = None

# Установите Windows Speech Platform как активный движок
recognizer.recognize_winapi = True

with sr.Microphone() as source:
    print("Скажите что-нибудь:")
    audio = recognizer.listen(source)

try:
    # Распознавание речи с использованием WSP
    text = recognizer.recognize_winapi(audio)
    print(f"Вы сказали: {text}")
except sr.UnknownValueError:
    print("Не удалось распознать речь")
except sr.RequestError as e:
    print(f"Ошибка при запросе к сервису распознавания: {e}")