import pytest

from pytest_django import fixtures
from selenium.webdriver import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functional_tests.base import wait_for_row_in_list_table, browser, get_item_input_box

wait = WebDriverWait(browser, timeout=3)


class TestItemValidation:
    """Тест: нельзя добавлять пустые элементы списка"""

    # @pytest.mark.skip
    def test_cannot_add_empty_list_items(self, browser: webdriver.Chrome, live_server: fixtures.live_server):
        """Тест: нельзя добавлять пустые элементы списка"""
        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        browser.get(live_server.url)
        input_box = get_item_input_box(browser)
        input_box.send_keys(Keys.ENTER)

        # Браузер перехватывает запрос и не загружает страницу со списком
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_text:invalid"))
        )
        # Эдит начинает набирать текст нового элемента и ошибка исчезает
        input_box = get_item_input_box(browser)
        input_box.send_keys("Buy milk")
        WebDriverWait(browser, 5).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_text:invalid"))
        )
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_text:valid"))
        )
        # И она может отправить его успешно
        input_box = get_item_input_box(browser)
        input_box.send_keys(Keys.ENTER)
        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        input_box = get_item_input_box(browser)
        input_box.send_keys(Keys.ENTER)
        # И снова браузер не подчинится
        wait_for_row_in_list_table("1: Buy milk", browser)
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_text:invalid"))
        )
        # И она может исправиться, заполнив поле текстом
        input_box = get_item_input_box(browser)
        input_box.send_keys("Make tea")
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_text:valid"))
        )
        input_box.send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: Buy milk", browser)
        wait_for_row_in_list_table("2: Make tea", browser)
