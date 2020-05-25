"""второй трекер
"""
from datetime import date

from gii_torrents import settings
from gii_torrents.loaders.base import BaseTrackerLoader


class Tracker2(BaseTrackerLoader):
    """второй трекер
    """

    CONFIG_FILE_NAME = 'tracker2_settings.yaml'
    OLD_CATEGORIES_FILE_NAME = 'tracker2_category_old.yaml'

    @staticmethod
    def get_pre_process_topic_date(topic_date_str: str) -> date:
        """парсим строку даты топика
        :param topic_date_str: дата топика, строка
        """
        try:
            d, m, y, _ = topic_date_str.split(maxsplit=3)
        except ValueError:
            print(topic_date_str)
            raise
        m_number = settings.MONTHS[m.lower().strip()]
        return date(int(y), m_number, int(d))

    @staticmethod
    def get_process_topic_date(topic_date_str: str) -> date:
        """парсим строку даты топика
        :param topic_date_str: дата топика, строка
        """
        return Tracker2.get_pre_process_topic_date(topic_date_str)
