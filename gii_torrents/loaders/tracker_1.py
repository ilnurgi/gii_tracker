"""первый трекер
"""

from time import sleep

from selenium.webdriver.remote.webdriver import WebDriver

from gii_torrents import settings
from gii_torrents.helpers import log_method, load_url
from gii_torrents.loaders.base import BaseTrackerLoader


class Tracker1(BaseTrackerLoader):
    """первый трекер
    """

    CONFIG_FILE_NAME = 'tracker1_settings.yaml'
    OLD_CATEGORIES_FILE_NAME = 'tracker1_category_old.yaml'

    def __init__(self, browser: WebDriver):
        """инициализация экземпляра
        """

        self.AUTH_URL = None
        self.AUTH_S1 = None
        self.AUTH_S2 = None
        self.AUTH_S3 = None
        self.AUTH_S4 = None

        self.LOGIN = None
        self.PASSWORD = None

        self.CONFIG_LOAD_KEYS += (
            'AUTH_URL', 'LOGIN', 'PASSWORD',
            'AUTH_S1', 'AUTH_S2', 'AUTH_S3', 'AUTH_S4',
        )

        super(Tracker1, self).__init__(browser)

    @log_method
    def auth(self):
        """авторизация
        """
        load_url(self.browser, self.AUTH_URL, count=3)

        form = self.browser.find_element_by_id(self.AUTH_S1)

        input_ = form.find_element_by_name(self.AUTH_S2)
        input_.send_keys(self.LOGIN)
        sleep(1)

        if not self.PASSWORD:
            input('Жду авторизации...')
            return

        input_ = form.find_element_by_name(self.AUTH_S3)
        input_.send_keys(self.PASSWORD)
        sleep(1)

        input_ = form.find_element_by_name(self.AUTH_S4)
        input_.click()
        sleep(1)
