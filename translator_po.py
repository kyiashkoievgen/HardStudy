import polib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def translate_po_file(input_file_path, output_file_path):
    # Загрузка .po файла
    po = polib.pofile(input_file_path)

    # Перевод каждой записи
    for entry in po:
        if not entry.translated():
            response = client.chat.completions.create(
                temperature=0.5,
                max_tokens=1000,
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a translator."},
                    {"role": "user", "content": f"translate from ru to pt:{entry.msgid}"}]
            )
            # Здесь должен быть ваш механизм перевода, например, вызов внешнего API
            # translator - это функция, которую вы определяете для перевода строки
            entry.msgstr = response.choices[0].message.content
            print(response.choices[0].message.content)

    # Сохранение измененного .po файла
    po.save(output_file_path)


translate_po_file('C:\\Users\\User\\Documents\\project\\HardStudy\\web\\translations\\pt\\LC_MESSAGES\\messages.po', 'C:\\Users\\User\\Documents\\project\\HardStudy\\web\\translations\\pt\\LC_MESSAGES\\messages.po')
