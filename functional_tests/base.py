import os
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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


def wait(fn):
    """Декоратор ожидания"""

    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > 5:
                    raise e
                time.sleep(0.5)

    return modified_fn


@wait
def wait_for_row_in_list_table(row_text, browser: webdriver.Chrome):
    """Ожидать строку в таблице списка."""
    table = browser.find_element(By.ID, "id_list_table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert row_text in [row.text for row in rows]


def get_item_input_box(browser: webdriver.Chrome):
    """Получить поле ввода для элемента."""
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


def add_list_item(item_text, browser):
    """Добавить элемент списка."""
    try:
        num_rows = len(browser.find_elements(By.CSS_SELECTOR, "#id_list_table tr"))
        print(num_rows)
    except NoSuchElementException as e:
        print(e)
        num_rows = 0
    get_item_input_box(browser).send_keys(item_text)
    get_item_input_box(browser).send_keys(Keys.ENTER)
    item_number = num_rows + 1
    print(f"{item_number}: {item_text}")
    wait_for_row_in_list_table(f"{item_number}: {item_text}", browser)


if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
