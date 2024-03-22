import os

from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from blockcypher import get_address_details
from dotenv import load_dotenv
import qrcode
import base64
from io import BytesIO

from web import db
from web.hard_study.modls import TransactionHistory

load_dotenv()
walled_name = os.getenv('SECRET_KEY')


def create_wallet():
    passphrase = Mnemonic().generate()
    print("Сид-фраза нового кошелька:", passphrase)
    w = Wallet.create(walled_name, keys=passphrase, witness_type='segwit', network='bitcoin')
    print(w.info())


def get_wallet_info():
    w = Wallet(walled_name)
    print(w.info())


def get_new_address():
    w = Wallet(walled_name)
    key = w.new_key()
    return key.address


def get_all_address():
    w = Wallet(walled_name)
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
        'btc_balance': 0
    }
    address_info = get_address_details(user.btc_address)
    if address_info['unconfirmed_balance'] > 0:
        user_balance['btc_transaction_in_progress'] = address_info['unconfirmed_balance']
    for transaction in address_info['txrefs']:
        if transaction['confirmations'] < 2:
            user_balance['unconfirmed_balance'] += transaction['value']
    user_bal_diff = (address_info['final_balance']-user_balance['unconfirmed_balance']) - user.user_btc_balance
    if user_bal_diff != 0:
        transaction_history = TransactionHistory(value=user_bal_diff, description="Пополнение" )
        user.user_btc_balance += user_bal_diff
        db.session.add(user)
        db.session.add(transaction_history)
        db.session.commit()
    user_balance['btc_balance'] = user.user_btc_balance - user.motivator_btc_balance - user.my_btc_balance
    return user_balance
