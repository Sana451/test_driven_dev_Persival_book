import os
import sys
import time
import re
import math

import pytest
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def browser():
    options = Options()
    options.add_argument('--headless=new')
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    staging_server = os.environ.get("STAGING_SERVER")
    if staging_server:
        browser.staging_url = "http://" + staging_server
    else:
        browser.staging_url = None
    yield browser
    browser.quit()


def wait_for_row_in_list_table(row_text, browser: webdriver.Chrome, max_wait=5):
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


# @pytest.mark.xfail(reason="assert False")
@pytest.mark.django_db
def test_can_start_a_list_for_one_user(browser, live_server):
    """Тест: можно начать список для одного пользователя."""
    # # live_server is a built-in Django-pytest Fixture (used instead of Django unittest.LiveServerTestCase)
    # Эдит слышала про крутое новое онлайн-приложение со списком
    # неотложных дел. Она решает оценить его домашнюю страницу
    staging_url = browser.staging_url
    browser.get(staging_url if staging_url else live_server.url)

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

    # Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
    # сайт сгенерировал для нее уникальный URL-адрес – об этом
    # выводится небольшой текст с объяснениями.

    # Она посещает этот URL-адрес – ее список по-прежнему там.

    # Удовлетворенная, она снова ложится спать


@pytest.mark.django_db
def test_multiple_users_can_start_lists_at_different_urls(browser, live_server):
    """Тест: многочисленные пользователи могут начать списки по разным url."""
    # Эдит начинает новый список
    staging_url = browser.staging_url
    browser.get(staging_url if staging_url else live_server.url)
    inputbox = browser.find_element(By.ID, "id_new_item")
    inputbox.send_keys('Купить павлиньи перья')
    inputbox.send_keys(Keys.ENTER)
    wait_for_row_in_list_table('1: Купить павлиньи перья', browser)
    # Она замечает, что ее список имеет уникальный URL-адрес
    edith_list_url = browser.current_url
    assert re.match(r".+/lists/.+", edith_list_url)

    # Теперь новый пользователь, Фрэнсис, приходит на сайт.
    # # Мы используем новый сеанс браузера, тем самым обеспечивая, чтобы никакая
    # # информация от Эдит не прошла через данные cookie и пр.
    browser.quit()
    options = Options()
    options.add_argument('--headless=new')
    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
    # Фрэнсис посещает домашнюю страницу. Нет никаких признаков списка Эдит
    browser.get(staging_url if staging_url else live_server.url)
    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert "Купить павлиньи перья" not in page_text
    assert "Сделать мушку" not in page_text

    # Фрэнсис начинает новый список, вводя новый элемент. Он менее
    # интересен, чем список Эдит...
    inputbox = browser.find_element(By.ID, "id_new_item")
    inputbox.send_keys('Купить молоко')
    inputbox.send_keys(Keys.ENTER)
    wait_for_row_in_list_table('1: Купить молоко', browser)

    # Фрэнсис получает уникальный URL-адрес
    francis_list_url = browser.current_url
    assert re.match(r".+/lists/.+", francis_list_url)
    assert francis_list_url != edith_list_url

    # Опять-таки, нет ни следа от списка Эдит
    page_text = browser.find_element(By.TAG_NAME, "body").text
    assert 'Купить павлиньи перья' not in page_text
    assert 'Купить молоко' in page_text

    # Удовлетворенные, они оба ложатся спать


class TestNewVisitor:
    """Тест нового посетителя"""

    def test_layout_and_styling(self, browser, live_server):
        """Тест макета и стилевого оформления"""
        # Эдит открывает домашнюю страницу
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        browser.set_window_size(1024, 768)
        # Она замечает, что поле ввода аккуратно центрировано
        inputbox = browser.find_element(By.ID, "id_new_item")

        assert math.isclose(
            a := 512,
            b := inputbox.location["x"] + inputbox.size["width"] / 2,
            rel_tol=0.02
        ), f"{a} != {b}, within {a * 0.02} delta"

        # # заголовок теперь имеет красный цвет (rgba 255, 0, 0, 1), похоже, что base.css загружен
        h1_to_do_title = browser.find_element(By.CSS_SELECTOR, ".text-center h1")
        h1_color = h1_to_do_title.value_of_css_property("color")
        assert h1_color == "rgba(255, 0, 0, 1)"

        # Она начинает новый список и видит, что поле ввода там
        # также находится по центру
        inputbox.send_keys("testing")
        inputbox.send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: testing", browser)

        inputbox = browser.find_element(By.ID, "id_new_item")

        assert math.isclose(
            a := 512,
            b := inputbox.location["x"] + inputbox.size["width"] / 2,
            rel_tol=0.02
        ), f"{a} != {b}, within {a * 0.02} delta"


if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
