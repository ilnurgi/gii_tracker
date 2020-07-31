"""базовый загрузчик данных
"""

import os

from datetime import datetime, date
from pprint import pprint

import yaml

from selenium.common.exceptions import JavascriptException
from selenium.webdriver.remote.webdriver import WebDriver

from gii_torrents import settings
from gii_torrents.helpers import log_method, load_url


class BaseTrackerLoader:
    """базовый загрузчик
    """
    CONFIG_FILE_NAME = None
    OLD_CATEGORIES_FILE_NAME = None

    CONFIG_LOAD_KEYS = (
        'CATEGORY_SCRIPT_1', 'CATEGORY_URL', 'CATEGORY_ENABLED_LINKS', 'LINKS_SCRIPT_1', 'TOPIC_SCRIPT_1',
        'TOPIC_EXCLUDE_TITLES_IN',
    )
    CATEGORY_URL = None
    CATEGORY_SCRIPT_1 = None
    LINKS_SCRIPT_1 = None
    TOPIC_SCRIPT_1 = None
    TOPIC_EXCLUDE_TITLES_IN = None

    def __init__(self, browser: WebDriver):
        """инициализация экземпляра
        """
        self.browser = browser

        assert self.CONFIG_FILE_NAME is not None, 'CONFIG_FILE_NAME must be set'
        assert self.OLD_CATEGORIES_FILE_NAME is not None, 'OLD_CATEGORIES_FILE_NAME must be set'

        self.CATEGORY_ENABLED_LINKS = {}

        self._load_config_file()
        self._topics = {}
        self._topics_errors = {}

    @property
    def category_topics(self) -> tuple:
        """возвращает сведения по категориям топиков
        """
        categories = {}
        for topic_link, topic_info in self._topics.items():
            categories.setdefault(
                (topic_info['category_link'], topic_info['category_title']), []
            ).append(
                (topic_link, topic_info['topic_title'])
            )
        for topic_link, topic_info in self._topics_errors.items():
            categories.setdefault(
                (topic_info['err_msg'], topic_info['err_msg']), []
            ).append(
                (topic_link, topic_info['topic_title'])
            )
        return tuple(sorted(categories.items(), key=lambda category_item: category_item[0][0]))

    def _load_config_file(self):
        """загрузка конфиг файла
        """
        config_file_path = os.path.join(settings.SETTINGS_DIR, self.CONFIG_FILE_NAME)
        assert os.path.exists(config_file_path), f'CONFIG_FILE not exists: {config_file_path}'

        with open(config_file_path, encoding='utf-8') as config_fh:
            config = yaml.safe_load(config_fh)

        for key, value in config.items():
            if key not in self.CONFIG_LOAD_KEYS:
                continue
            setattr(self, key, value)

    def _get_old_categories(self):
        """возвращает старые категории, которые уже были на трекере
        """
        old_categories_path = os.path.join(settings.SETTINGS_DIR, self.OLD_CATEGORIES_FILE_NAME)
        if not os.path.exists(old_categories_path):
            return {}

        return yaml.safe_load(open(old_categories_path, encoding='utf-8')) or {}

    @log_method
    def auth(self):
        """авторизация
        """

    @log_method
    def populate_category_links(self):
        """актуализация категории трекера
        """
        load_url(self.browser, self.CATEGORY_URL, 3)

        categories = self.browser.execute_script(self.CATEGORY_SCRIPT_1)
        exists_categories = {
            cat_link: cat_text
            for cat_link, cat_text in categories
        }
        old_categories = self._get_old_categories()
        new_categories = {
            cat_link: cat_text
            for cat_link, cat_text in exists_categories.items()
            if cat_link not in old_categories
        }
        if new_categories:
            print('new categories')
            pprint(new_categories)
            old_category_file_path = os.path.join(settings.SETTINGS_DIR, self.OLD_CATEGORIES_FILE_NAME)
            yaml.safe_dump(exists_categories, open(old_category_file_path, 'w', encoding='utf-8'), allow_unicode=True)

    @staticmethod
    def get_pre_process_topic_date(topic_date_str: str) -> date:
        """парсим строку даты топика
        :param topic_date_str: дата топика, строка
        """
        return datetime.strptime(topic_date_str, '%Y-%m-%d %H:%M').date()

    def pre_process_topics(self):
        """предварительный сбор топиков
        """
        pages_count = 10
        page_limit = 50

        max_year_prefix = '<<<'
        max_year_prefix_len = len(max_year_prefix)
        max_year_suffix = '>>>'
        max_year_suffix_len = len(max_year_suffix)
        for category_link, category_info in self.CATEGORY_ENABLED_LINKS.items():
            category_title = category_info['title']
            category_title_exclude_in = category_info.get('exclude_in', ())
            max_years = [
                exclude
                for exclude in category_title_exclude_in
                if str(exclude).startswith(max_year_prefix) and str(exclude).endswith(max_year_suffix)
            ]
            if max_years:
                max_year = int(max_years[0][max_year_prefix_len:-max_year_suffix_len])
                category_title_exclude_in.extend(range(1900, max_year))

            for page_number in range(0, pages_count*page_limit, page_limit):
                current_url = f'{category_link}&start={page_number}'
                # print(current_url, category_title)
                load_url(self.browser, current_url, count=3)

                topics = {}

                for topic_date_str, topic_url, topic_title in self.browser.execute_script(self.LINKS_SCRIPT_1):

                    if any(str(exclude).lower() in topic_title.lower() for exclude in category_title_exclude_in):
                        continue

                    if (
                            self.TOPIC_EXCLUDE_TITLES_IN and
                            any(
                                excl_in in topic_title.lower()
                                for excl_in in self.TOPIC_EXCLUDE_TITLES_IN
                            )
                    ):
                        continue

                    if not topic_date_str:
                        self._topics_errors[topic_url] = {
                            'topic_title': topic_title,
                            'err_msg': 'date is None'
                        }
                        print(f'ERROR: date is None, ({topic_date_str}, {topic_title}, {topic_url})')
                        continue

                    topic_date = self.get_pre_process_topic_date(topic_date_str)
                    if not (settings.CHECK_PERIOD_START <= topic_date <= settings.CHECK_PERIOD_END):
                        continue

                    topics[topic_url] = {
                        'topic_title': topic_title,
                        'category_title': category_title,
                        'category_link': category_link,
                    }

                if not topics:
                    break
                # for k, v in topics.items():
                #     print('\t', k, v['topic_title'])

                self._topics.update(topics)
                yield
            # break

    @staticmethod
    def get_process_topic_date(topic_date_str: str) -> date:
        """парсим строку даты топика
        :param topic_date_str: дата топика, строка
        """
        topic_date, _ = topic_date_str.split()
        d, m, y = topic_date.split('-')
        m_number = settings.MONTHS[m.lower().strip()]
        return date(2000 + int(y), m_number, int(d))

    def process_topics(self):
        """подробная обработка топика
        """
        topics_len = len(self._topics)
        for index, topic in enumerate(tuple(self._topics.items())):
            if index % 100 == 0:
                print(self.__class__.__name__, f'{index}/{topics_len}')

            topic_link, topic_info = topic
            topic_title = topic_info['topic_title']
            # print(topic_link, topic_title)
            try:
                load_url(self.browser, topic_link, count=3)
            except TimeoutError:
                self._topics_errors[topic_link] = {
                    'topic_title': topic_title,
                    'err_msg': 'timeout'
                }
                print(f'ERROR, timeout: {topic_link}, {topic_title}')
                self._topics.pop(topic_link)
                continue

            try:
                topic_datetime = self.browser.execute_script(self.TOPIC_SCRIPT_1)
            except JavascriptException:
                self._topics_errors[topic_link] = {
                    'topic_title': topic_title,
                    'err_msg': 'js'
                }
                print(f'ERROR, js: {topic_link}, {topic_title}')
                self._topics.pop(topic_link)
                continue

            topic_date = self.get_process_topic_date(topic_datetime)
            if not (settings.CHECK_PERIOD_START <= topic_date <= settings.CHECK_PERIOD_END):
                self._topics.pop(topic_link)
            yield
