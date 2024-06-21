import pytest
from selenium.common import TimeoutException

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functional_tests.base import wait_for_row_in_list_table, browser
from pytest_django.fixtures import live_server

wait = WebDriverWait(browser, timeout=3)


class TestItemValidation:
    """Тест: нельзя добавлять пустые элементы списка"""

    # @pytest.mark.skip
    def test_cannot_add_empty_list_items(self, browser, live_server):
        """Тест: нельзя добавлять пустые элементы списка"""
        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        browser.get(live_server.url)
        browser.find_element(By.ID, "id_new_item").send_keys(Keys.ENTER)
        # Домашняя страница обновляется, и появляется сообщение об ошибке,
        # которое говорит, что элементы списка не должны быть пустыми
        error_element = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "has-error"))
        )
        assert error_element
        # Она пробует снова, теперь с неким текстом для элемента, и теперь
        browser.find_element(By.ID, "id_new_item").send_keys("Buy milk")
        wait_for_row_in_list_table("1: Buy milk")
        # это срабатывает
        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        browser.find_element(By.ID, "id_new_item").send_keys(Keys.ENTER)
        # Она получает аналогичное предупреждение на странице списка
        error_element = WebDriverWait(browser, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "has-error"))
        )
        assert error_element
        # И она может его исправить, заполнив поле неким текстом
        browser.find_element(By.ID, "id_new_item").send_keys("Make tea")
        wait_for_row_in_list_table("1: Buy milk")
        wait_for_row_in_list_table("2: Make tea")
