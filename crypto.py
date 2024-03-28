import os

import requests
from bitcoinlib.wallets import Wallet, wallet_create_or_open
from bitcoinlib.mnemonic import Mnemonic
from blockcypher import get_address_details, list_webhooks, subscribe_to_address_webhook
from dotenv import load_dotenv
import qrcode
import base64
from io import BytesIO

from web import db

load_dotenv()
walled_name = os.getenv('WALLED_NAME')
db_uri = os.getenv('BITCOINLIB_DATABASE_URI')


def create_wallet():
    passphrase = Mnemonic().generate()
    print("Сид-фраза нового кошелька:", passphrase)
    w = Wallet.create(walled_name, keys=passphrase, witness_type='segwit', network='bitcoin', db_uri=db_uri)
    print(w.info())


# Функция для создания нового кошелька из сид-фразы в базе данных
def create_wallet_from_seed(seed):
    w = wallet_create_or_open(walled_name, keys=seed, witness_type='segwit', network='bitcoin', db_uri=db_uri)
    return w.info()


def get_wallet_info():
    w = Wallet(walled_name, db_uri=db_uri)
    print(w.info())


def get_new_address():
    w = Wallet(walled_name, db_uri=db_uri)
    key = w.new_key()
    return key.address


def get_all_address():
    w = Wallet(walled_name, db_uri=db_uri)
    keys = w.keys()
    return [key.address for key in keys]


def qrcode_gen(address):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(address)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Преобразование изображения QR-кода в строку base64 для передачи в шаблон
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()


def get_user_balance(user):
    user_balance = {
        'unconfirmed_balance': 0,
        'btc_transaction_in_progress': 0,
        'btc_balance': user.user_btc_balance
    }
    # address_info = get_address_details(user.btc_address)
    # if address_info['unconfirmed_balance'] > 0:
    #     user_balance['btc_transaction_in_progress'] = address_info['unconfirmed_balance']
    # for transaction in address_info['txrefs']:
    #     if transaction['confirmations'] < 2:
    #         user_balance['unconfirmed_balance'] += transaction['value']
    # user_bal_diff = (address_info['final_balance'] - user_balance['unconfirmed_balance']) - user.user_btc_balance
    # if user_bal_diff != 0:
    #     from web.hard_study.modls import TransactionHistory
    #     transaction_history = TransactionHistory(value=user_bal_diff, description="Пополнение")
    #     user.user_btc_balance += user_bal_diff
    #     db.session.add(user)
    #     db.session.add(transaction_history)
    #     db.session.commit()
    user_balance['btc_balance'] = user.user_btc_balance - user.motivator_btc_balance - user.my_btc_balance
    return user_balance


# функция для отображения цены биткоина в выбранных валютах
# функция принимает на вход валюту на которую нужно перевести цену биткоина и колчество биткоинов сатоши
# возвращает цену биткоина в выбранной валюте
def btc_price_converter(currency_user, amount, to_btc=False):
    btc_price = currency_user.currency_rate
    if to_btc:
        return amount / btc_price * 100000000
    else:
        return btc_price * amount / 100000000


def get_btc_rate(currency_user):
    try:
        user_currency = currency_user.currency_show
        if user_currency == 'Sat':
            currency = 'BTC'
        else:
            currency = user_currency
        url = f'https://api.coindesk.com/v1/bpi/currentprice/{currency}.json'
        response = requests.get(url)
        response.raise_for_status()  # Поднимает исключение для ответов с ошибкой
        response_json = response.json()
        btc_price = response_json['bpi'][currency]['rate_float']
        if user_currency == 'Sat':
            btc_price = btc_price*100000000
        return btc_price
    except Exception as e:
        # Здесь можно добавить логирование или другую обработку ошибки
        return None


# функция для которая возвращает список валют доступных в coindesk
def get_currency_list():
    url = 'https://api.coindesk.com/v1/bpi/supported-currencies.json'
    response = requests.get(url)
    response_json = response.json()
    cur_list = [currency_list['currency'] for currency_list in response_json]
    cur_list.append('Sat')
    return cur_list


def check_webhook_existence(address, api_key):
    # Функция для проверки существующих веб-хуков для адреса
    # Это псевдокод, вам нужно адаптировать его под используемый API
    existing_webhooks = list_webhooks(api_key)  # Получение списка веб-хуков
    for webhook in existing_webhooks:
        if webhook['address'] == address:
            return True
    return False


def create_webhook_if_not_exists(address, callback_url, api_key):
    if not check_webhook_existence(address, api_key):
        subscribe_to_address_webhook(callback_url=callback_url,
                                     subscription_address=address,
                                     api_key=api_key)
