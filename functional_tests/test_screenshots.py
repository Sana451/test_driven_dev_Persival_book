import os
from datetime import datetime

import pytest
from pytest_django.fixtures import live_server
from functional_tests.base import browser

SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "screendumps"
)


class TestScreen:

    def get_filename(self):
        """Получить имя файла."""
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return "{folder}/{classname}-{timestamp}".format(
            folder=SCREEN_DUMP_LOCATION,
            classname=__name__,
            timestamp=timestamp
        )

    def test_can_get_screenshot(self, browser, live_server):
        """Тест:."""
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        # сделать скрин
        png_filename = self.get_filename() + ".png"
        print("screenshotting to", png_filename)
        browser.save_screenshot(png_filename)
        # сохранить html код страницы
        html_filename = self.get_filename() + ".html"
        print("dumping page HTML to", html_filename)
        with open(html_filename, "w") as f:
            f.write(browser.page_source)
