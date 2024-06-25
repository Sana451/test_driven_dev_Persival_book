import re

import pytest
from pytest_django.fixtures import live_server
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from functional_tests.base import wait_for_row_in_list_table, browser, get_item_input_box


class TestNewVisitor:
    """Тест нового посетителя"""

    # @pytest.mark.xfail(reason="assert False")
    @pytest.mark.django_db
    def test_can_start_a_list_for_one_user(self, browser, live_server):
        """Тест: можно начать список для одного пользователя."""
        # # live_server is a built-in Django-pytest Fixture (used instead of Django unittest.LiveServerTestCase)
        # Эдит слышала про крутое новое онлайн-приложение со списком
        # неотложных дел. Она решает оценить его домашнюю страницу
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)

        # Она видит, что заголовок и шапка страницы говорят о списках
        # неотложных дел
        assert "To-Do" in browser.title, "Browser title was " + browser.title

        input_box = get_item_input_box(browser)
        assert input_box.get_attribute("placeholder") == "Enter a to-do item"
        # Ей сразу же предлагается ввести элемент списка
        # Она набирает в текстовом поле "Купить павлиньи перья" (ее хобби –
        # вязание рыболовных мушек)
        input_box.send_keys("Купить павлиньи перья")
        # Когда она нажимает enter, страница обновляется, и теперь страница
        # содержит "1: Купить павлиньи перья" в качестве элемента списка
        input_box.send_keys(Keys.ENTER)

        wait_for_row_in_list_table('1: Купить павлиньи перья', browser)

        # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
        # Она вводит "Сделать мушку из павлиньих перьев"
        # (Эдит очень методична)
        input_box = get_item_input_box(browser)
        input_box.send_keys("Сделать мушку из павлиньих перьев")
        input_box.send_keys(Keys.ENTER)

        # Страница снова обновляется, и теперь показывает оба элемента ее списка
        wait_for_row_in_list_table("1: Купить павлиньи перья", browser)
        wait_for_row_in_list_table("2: Сделать мушку из павлиньих перьев", browser)

        # Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
        # сайт сгенерировал для нее уникальный URL-адрес – об этом
        # выводится небольшой текст с объяснениями.

        # Она посещает этот URL-адрес – ее список по-прежнему там.

        # Удовлетворенная, она снова ложится спать

    @pytest.mark.django_db
    def test_multiple_users_can_start_lists_at_different_urls(self, browser, live_server):
        """Тест: многочисленные пользователи могут начать списки по разным url."""
        # Эдит начинает новый список
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        inputbox = get_item_input_box(browser)
        inputbox.send_keys("Купить павлиньи перья")
        inputbox.send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Купить павлиньи перья", browser)
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
        inputbox = get_item_input_box(browser)
        inputbox.send_keys("Купить молоко")
        inputbox.send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Купить молоко", browser)

        # Фрэнсис получает уникальный URL-адрес
        francis_list_url = browser.current_url
        assert re.match(r".+/lists/.+", francis_list_url)
        assert francis_list_url != edith_list_url

        # Опять-таки, нет ни следа от списка Эдит
        page_text = browser.find_element(By.TAG_NAME, "body").text
        assert 'Купить павлиньи перья' not in page_text
        assert 'Купить молоко' in page_text

        # Удовлетворенные, они оба ложатся спать
