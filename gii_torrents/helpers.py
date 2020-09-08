"""хелперы
"""

from time import sleep

from selenium.common.exceptions import TimeoutException, WebDriverException

from gii_torrents import settings


def log_method(method):
    """простой логер работы
    """
    def inner(*args, **kwargs):
        self = args[0]
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(f'-> START: {class_name}, {method_name}')
        result = method(*args, **kwargs)
        print(f'--> DONE: {class_name}, {method_name}')
        return result
    return inner


def load_url(browser, url, count):
    """загружает страницу в браузере
    :param browser: селениум браузер
    :param url: адрес страницы
    :param count: количество попыток
    """
    for step in range(count):
        try:
            browser.get(url)
        except (TimeoutError, TimeoutException, WebDriverException):
            continue
        sleep(settings.REQUEST_TIMEOUT + step)
        break
    else:
        # вышли без брейк, значит страница не загрузилась
        print(url)
        raise TimeoutError()
