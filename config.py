import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class LanguageCurrencyConfig:
    currency_by_language = {
        'de-DE': 'EUR',  # Немецкий (Германия) -> Евро
        'fr-FR': 'EUR',  # Французский (Франция) -> Евро
        'es-ES': 'EUR',  # Испанский (Испания) -> Евро
        'it-IT': 'EUR',  # Итальянский (Италия) -> Евро
        'nl-NL': 'EUR',  # Нидерландский (Нидерланды) -> Евро
        'pt-PT': 'EUR',  # Португальский (Португалия) -> Евро
        'el-GR': 'EUR',  # Греческий (Греция) -> Евро
        'fi-FI': 'EUR',  # Финский (Финляндия) -> Евро
        'sv-SE': 'SEK',  # Шведский (Швеция) -> Шведская крона
        'da-DK': 'DKK',  # Датский (Дания) -> Датская крона
        'pl-PL': 'PLN',  # Польский (Польша) -> Польский злотый
        'cs-CZ': 'CZK',  # Чешский (Чехия) -> Чешская крона
        'hu-HU': 'HUF',  # Венгерский (Венгрия) -> Венгерский форинт
        'ro-RO': 'RON',  # Румынский (Румыния) -> Румынский лей
        'bg-BG': 'BGN',  # Болгарский (Болгария) -> Болгарский лев
        'en-GB': 'GBP',  # Английский (Великобритания) -> Британский фунт
        'hr-HR': 'HRK',  # Хорватский (Хорватия) -> Хорватская куна
        'lt-LT': 'EUR',  # Литовский (Литва) -> Евро
        'lv-LV': 'EUR',  # Латышский (Латвия) -> Евро
        'et-EE': 'EUR',  # Эстонский (Эстония) -> Евро
        'mt-MT': 'EUR',  # Мальтийский (Мальта) -> Евро
        'sk-SK': 'EUR',  # Словацкий (Словакия) -> Евро
        'sl-SI': 'EUR',  # Словенский (Словения) -> Евро
        'ru-RU': 'RUB',  # Русский (Россия) -> Российский рубль
        'uk-UA': 'UAH',  # Украинский (Украина) -> Украинская гривна
        'be-BY': 'BYN',  # Белорусский (Беларусь) -> Белорусский рубль
        'kk-KZ': 'KZT',  # Казахский (Казахстан) -> Казахский тенге
        'ky-KG': 'KGS',  # Киргизский (Киргизия) -> Киргизский сом
        'uz-UZ': 'UZS',  # Узбекский (Узбекистан) -> Узбекский сум
        'mn-MN': 'MNT',  # Монгольский (Монголия) -> Монгольский тугрик
        'ka-GE': 'GEL',  # Грузинский (Грузия) -> Грузинский лари
        'hy-AM': 'AMD',  # Армянский (Армения) -> Армянский драм
        'he-IL': 'ILS',  # Иврит (Израиль) -> Израильский шекель
        'ar-IL': 'ILS',  # Арабский (Израиль) -> Израильский шекель
        'tr-TR': 'TRY',  # Турецкий (Турция) -> Турецкая лира
        'fa-IR': 'IRR',  # Персидский (Иран) -> Иранский риал
        'ur-PK': 'PKR',  # Урду (Пакистан) -> Пакистанская рупия
        'hi-IN': 'INR',  # Хинди (Индия) -> Индийская рупия
        'bn-IN': 'INR',  # Бенгальский (Индия) -> Индийская рупия
    }


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_TIME_LIMIT = 43200
    # BOOTSTRAP_SERVE_LOCAL = True
    LANGUAGES = ['ru', 'pt', 'es', 'en']
    MAIL_SUBJECT_PREFIX = 'Study Forge '
    MAIL_SENDER = os.getenv('MAIL_USERNAME')

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
