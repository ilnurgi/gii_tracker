"""конфигурация приложения
"""

import os

from datetime import date, timedelta

import yaml

HOME_DIR = os.path.expanduser('~')
SETTINGS_DIR = os.path.join(HOME_DIR, 'gii_torrents_settings')

LOGS_DIR = os.path.join(SETTINGS_DIR, 'logs')
NUMBERS_PATH = os.path.join(LOGS_DIR, 'numbers.yaml')
CHROME_DRIVER_PATH = os.path.join(SETTINGS_DIR, 'chromedriver.exe')

os.makedirs(SETTINGS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LAST_CHECK = date.today() - timedelta(days=7)
PAGE_LOAD_TIMEOUT = 10
REQUEST_TIMEOUT = 1
CHECK_PERIOD_DAYS = 0

CHROME_PROXY_EXTENSION_PATH = ''

MONTHS = {
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'май': 5,
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}

__load_keys = (
    'LAST_CHECK', 'PAGE_LOAD_TIMEOUT', 'REQUEST_TIMEOUT', 'CHROME_PROXY_EXTENSION_PATH', 'CHECK_PERIOD_DAYS',
)


def create_example_settings():
    """создаем пример файлов настроек
    """
    example_path = os.path.join(SETTINGS_DIR, 'example_settings.yaml')
    if os.path.exists(example_path):
        return

    yaml.dump(dict.fromkeys(__load_keys), open(os.path.join(example_path), 'w'))


def load():
    """загрузка конфигурации
    """
    settings_file_path = os.path.join(SETTINGS_DIR, 'settings.yaml')
    with open(settings_file_path, encoding='utf-8') as settings_file:
        custom_settings_yaml = yaml.safe_load(settings_file) or {}

    custom_settings = {
        key: custom_settings_yaml[key]
        for key in __load_keys if key in custom_settings_yaml
    }
    globals().update(custom_settings)


def save(**kwargs):
    """сохраняем конфигурацию
    """
    settings_file_path = os.path.join(SETTINGS_DIR, 'settings.yaml')
    global_settings = globals()
    save_settings = {
        key: global_settings[key]
        for key in __load_keys
    }
    save_settings.update({
        key: value for key, value in kwargs.items() if key in __load_keys
    })
    yaml.safe_dump(
        save_settings,
        open(settings_file_path, 'w', encoding='utf-8'),
        indent=2,
        allow_unicode=False
    )


load()
create_example_settings()

CHECK_PERIOD_START = LAST_CHECK
CHECK_PERIOD_END = (
        LAST_CHECK + timedelta(days=CHECK_PERIOD_DAYS)
        if CHECK_PERIOD_DAYS else date.today()
)
