import pytest

from pytest_django import fixtures
from selenium.webdriver import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functional_tests.base import (wait_for_row_in_list_table,
                                   browser,
                                   get_item_input_box,
                                   DUPLICATE_ITEM_ERROR,
                                   wait_until_presence_of_element,
                                   wait_until_NOT_presence_of_element)

wait = WebDriverWait(browser, timeout=3)


class TestItemValidation:

    def test_cannot_add_empty_list_items(self, browser: webdriver.Chrome, live_server: fixtures.live_server):
        """Тест: нельзя добавлять пустые элементы в список."""
        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        get_item_input_box(browser).send_keys(Keys.ENTER)
        # Браузер перехватывает запрос и не загружает страницу со списком
        wait_until_presence_of_element(browser, "#id_text:invalid")
        # Эдит начинает набирать текст нового элемента и ошибка исчезает
        get_item_input_box(browser).send_keys("Buy milk")
        wait_until_NOT_presence_of_element(browser, "#id_text:invalid")
        wait_until_presence_of_element(browser, "#id_text:valid")
        # И она может отправить его успешно
        get_item_input_box(browser).send_keys(Keys.ENTER)
        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        get_item_input_box(browser).send_keys(Keys.ENTER)
        # И снова браузер не подчинится
        wait_for_row_in_list_table("1: Buy milk", browser)
        wait_until_presence_of_element(browser, "#id_text:invalid")
        # И она может исправиться, заполнив поле текстом
        get_item_input_box(browser).send_keys("Make tea")
        wait_until_presence_of_element(browser, "#id_text:valid")
        get_item_input_box(browser).send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Buy milk", browser)
        wait_for_row_in_list_table("2: Make tea", browser)

    # @pytest.mark.skip
    def test_cannot_add_duplicate_items(self, browser: webdriver.Chrome, live_server: fixtures.live_server):
        """Тест: нельзя добавлять повторяющиеся элементы."""
        # Эдит открывает домашнюю страницу и начинает новый список
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        get_item_input_box(browser).send_keys("Buy wellies")
        get_item_input_box(browser).send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Buy wellies", browser)
        # Она случайно пытается ввести повторяющийся элемент
        get_item_input_box(browser).send_keys("Buy wellies")
        get_item_input_box(browser).send_keys(Keys.ENTER)
        # Она видит полезное сообщение об ошибке
        error_element = wait_until_presence_of_element(browser, ".has-error")
        assert error_element.text == DUPLICATE_ITEM_ERROR

    # @pytest.mark.skip
    def test_error_messages_are_cleared_on_input(self, browser: webdriver.Chrome, live_server: fixtures.live_server):
        """Тест: сообщения об ошибках очищаются при вводе."""
        # Эдит начинает список и вызывает ошибку валидации:
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        get_item_input_box(browser).send_keys("Banter too thick")
        get_item_input_box(browser).send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Banter too thick", browser)
        get_item_input_box(browser).send_keys("Banter too thick")
        get_item_input_box(browser).send_keys(Keys.ENTER)
        error_element = wait_until_presence_of_element(browser, ".has-error")
        assert error_element.is_displayed() is True
        # Она начинает набирать в поле ввода, чтобы очистить ошибку
        get_item_input_box(browser).send_keys("a")
        # Она довольна от того, что сообщение об ошибке исчезает
        error_element = wait_until_presence_of_element(browser, ".has-error")
        assert error_element.is_displayed() is False
