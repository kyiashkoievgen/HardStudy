import json

from flask import Flask, render_template, request, redirect, url_for, flash
from study import Study, Phrase
from db import DB

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/index')
def index():
    db = DB()
    json_data = json.dumps(dict(db.app_setting_init()))
    print(json_data)
    return render_template('layout.html', jsonStr=dict(db.app_setting_init()))

@app.route('/home')
def home():
    return render_template('content_home.html')

@app.route('/about')
def about():
    return render_template('content_about.html')

@app.route('/settings')
def settings():
    return render_template('setting.html')

@app.route('/process', methods=['POST'])
def process_form():
    name = request.form.get('name')
    email = request.form.get('email')

    if not name or not email:
        flash('Пожалуйста, заполните все поля!')
        return redirect(url_for('settings'))

    # Здесь можно провести дальнейшую обработку данных, например, сохранить в базе данных
    flash(f'Данные получены! Имя: {name}, Email: {email}')
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True)