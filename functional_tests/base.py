import os
import sys
import time

import pytest
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore

DUPLICATE_ITEM_ERROR = "You've already got this in your list"


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


def get_item_input_box(browser: webdriver.Chrome):
    """Получить поле ввода для элемента."""
    # return browser.find_element(By.ID, "id_new_item")
    return browser.find_element(By.ID, "id_text")


def wait_until_presence_of_element(browser: webdriver.Chrome, selector: str, by=By.CSS_SELECTOR):
    """Подождать пока элемент появится на странице."""
    error_element = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((by, selector))
    )
    return error_element


def wait_until_NOT_presence_of_element(browser: webdriver.Chrome, selector: str, by=By.CSS_SELECTOR):
    """Подождать пока элемент не исчезнет со страницы."""
    error_element = WebDriverWait(browser, 5).until_not(
        EC.presence_of_element_located((by, selector))
    )
    return error_element





if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
