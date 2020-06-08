"""приложения для сбора сведений по новым торент файлам
"""

import os
import webbrowser

from datetime import date

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver import Chrome, ChromeOptions

from gii_torrents import settings
from gii_torrents.loaders.tracker_1 import Tracker1
from gii_torrents.loaders.tracker_2 import Tracker2


def get_browser() -> Chrome:
    """возвращает браузер
    """
    if settings.CHROME_PROXY_EXTENSION_PATH:
        browser_options = ChromeOptions()
        browser_options.add_argument(f'load-extension={settings.CHROME_PROXY_EXTENSION_PATH}')
    else:
        browser_options = None

    browser = Chrome(settings.CHROME_DRIVER_PATH, options=browser_options)
    browser.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)

    input('Жду включения проксей...')

    for window_handle in browser.window_handles:
        try:
            browser.switch_to.window(window_handle)
        except NoSuchWindowException:
            pass
        else:
            break

    return browser


def pre_process_topics(tracker1: Tracker1, tracker2: Tracker2):
    """предварительная обработка урлов
    """
    tracker1_pre_process_topics = True
    tracker2_pre_process_topics = True

    tracker1_pre_process_topics_generator = tracker1.pre_process_topics()
    tracker2_pre_process_topics_generator = tracker2.pre_process_topics()

    print('-> START: pre_process_topics')
    while tracker1_pre_process_topics or tracker2_pre_process_topics:

        if tracker1_pre_process_topics:
            try:
                next(tracker1_pre_process_topics_generator)
            except StopIteration:
                tracker1_pre_process_topics = False

        if tracker2_pre_process_topics:
            try:
                next(tracker2_pre_process_topics_generator)
            except StopIteration:
                tracker2_pre_process_topics = False
    print('--> DONE: pre_process_topics')


def process_topics(tracker1: Tracker1, tracker2: Tracker2):
    """основная обработка урлов
    """
    tracker1_process_topics = True
    tracker2_process_topics = True

    tracker1_process_topics_generator = tracker1.process_topics()
    tracker2_process_topics_generator = tracker2.process_topics()

    print('-> START: process_topics')
    while tracker1_process_topics or tracker2_process_topics:

        if tracker1_process_topics:
            try:
                next(tracker1_process_topics_generator)
            except StopIteration:
                tracker1_process_topics = False

        if tracker2_process_topics:
            try:
                next(tracker2_process_topics_generator)
            except StopIteration:
                tracker2_process_topics = False
    print('--> DONE: process_topics')


def save_topics(tracker1: Tracker1, tracker2: Tracker2):
    """сохраняем полученные урлы
    """
    html_body = ''
    for tracker in (tracker1, tracker2):
        for category_info, category_topics in tracker.category_topics:
            category_link, category_title = category_info
            ul_topics = '<ul>{topics}</ul>'.format(
                topics=''.join(f'<li><a href="{link}">{title}</a></li>' for link, title in category_topics)
            )
            html_body += f'<ul><li><a href="{category_link}">{category_title}</a>{ul_topics}</li></ul>'
    doc_name = '{0}.html'.format(settings.CHECK_PERIOD_END.strftime('%Y.%m.%d'))
    doc_path = os.path.join(settings.LOGS_DIR, doc_name)
    open(doc_path, 'w', encoding='utf-8').write(
        f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"></head><body>{html_body}</body></html>'
    )
    webbrowser.open(f'file:///{doc_path}')


def main():
    """точка входа
    """
    if settings.LAST_CHECK == date.today():
        print('last check is today')
        exit(0)
    else:
        print('check period is', settings.CHECK_PERIOD_START, settings.CHECK_PERIOD_END)

    browser = get_browser()

    tracker1 = Tracker1(browser)
    tracker2 = Tracker2(browser)

    tracker1.auth()
    tracker2.auth()

    tracker1.populate_category_links()
    tracker2.populate_category_links()

    pre_process_topics(tracker1, tracker2)
    process_topics(tracker1, tracker2)
    save_topics(tracker1, tracker2)

    browser.close()
    settings.save(LAST_CHECK=settings.CHECK_PERIOD_END)


if __name__ == '__main__':
    main()
