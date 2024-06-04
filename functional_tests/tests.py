import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


MAX_WAIT = 10


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    yield browser
    browser.quit()


def wait_for_row_in_list_table(row_text, browser: webdriver.Chrome):
    """Ожидать строку в таблице списка"""
    start_time = time.time()
    while True:
        try:
            table = browser.find_element(By.ID, "id_list_table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            assert row_text in [row.text for row in rows]
            return
        except (AssertionError, WebDriverException) as e:
            if time.time() - start_time > MAX_WAIT:
                raise e
            time.sleep(0.5)


# @pytest.mark.xfail(reason="assert False")
@pytest.mark.django_db
def test_can_start_a_list_and_retrieve_it_later(browser, live_server):
    """Тест: можно начать список и получить его позже.
    live_server is a built-in Django-pytest Fixture (used instead of Django unittest.LiveServerTestCase)"""
    # Эдит слышала про крутое новое онлайн-приложение со списком
    # неотложных дел. Она решает оценить его домашнюю страницу
    browser.get(live_server.url)

    # Она видит, что заголовок и шапка страницы говорят о списках
    # неотложных дел
    assert "To-Do" in browser.title, "Browser title was " + browser.title

    inputbox = browser.find_element(By.ID, "id_new_item")
    assert inputbox.get_attribute("placeholder") == "Enter a to-do item"
    # Ей сразу же предлагается ввести элемент списка

    # Она набирает в текстовом поле "Купить павлиньи перья" (ее хобби –
    # вязание рыболовных мушек)
    inputbox.send_keys("Купить павлиньи перья")

    # Когда она нажимает enter, страница обновляется, и теперь страница
    # содержит "1: Купить павлиньи перья" в качестве элемента списка
    inputbox.send_keys(Keys.ENTER)

    wait_for_row_in_list_table('1: Купить павлиньи перья', browser)

    # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
    # Она вводит "Сделать мушку из павлиньих перьев"
    # (Эдит очень методична)
    inputbox = browser.find_element(By.ID, "id_new_item")
    inputbox.send_keys("Сделать мушку из павлиньих перьев")
    inputbox.send_keys(Keys.ENTER)

    # Страница снова обновляется, и теперь показывает оба элемента ее списка
    wait_for_row_in_list_table("1: Купить павлиньи перья", browser)
    wait_for_row_in_list_table("2: Сделать мушку из павлиньих перьев", browser)

    pytest.fail("End FTest")


# Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
# сайт сгенерировал для нее уникальный URL-адрес – об этом
# выводится небольшой текст с объяснениями.

# Она посещает этот URL-адрес – ее список по-прежнему там.

# Удовлетворенная, она снова ложится спать


if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
