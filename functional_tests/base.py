import os
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def browser():
    options = Options()
    headless = os.environ.get("HEADLESS")
    if not headless:
        options.add_argument('--headless=new')
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    staging_server = os.environ.get("STAGING_SERVER")
    if staging_server:
        browser.staging_url = "http://" + staging_server
    else:
        browser.staging_url = None
    yield browser
    browser.quit()


def wait_for_row_in_list_table(row_text, browser: webdriver.Chrome, max_wait=10):
    """Ожидать строку в таблице списка."""
    start_time = time.time()
    while True:
        try:
            table = browser.find_element(By.ID, "id_list_table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            assert row_text in [row.text for row in rows]
            return
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > max_wait:
                raise e
            time.sleep(0.5)


if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
