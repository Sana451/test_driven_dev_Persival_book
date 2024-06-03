import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


@pytest.fixture
def browser():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


def check_for_row_in_list_table(row_text, browser: webdriver.Chrome):
    """Подтверждение строки в таблице списка"""
    table = browser.find_element(By.ID, "id_list_table")
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert row_text in [row.text for row in rows]


# @pytest.mark.xfail
def test_can_start_a_list_and_retrieve_it_later(browser):
    """Тест: можно начать список и получить его позже"""
    # Эдит слышала про крутое новое онлайн-приложение со списком
    # неотложных дел. Она решает оценить его домашнюю страницу
    browser.get('http://localhost:8000')

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
    time.sleep(1)

    check_for_row_in_list_table('1: Купить павлиньи перья', browser)

    # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
    # Она вводит "Сделать мушку из павлиньих перьев"
    # (Эдит очень методична)
    inputbox = browser.find_element(By.ID, "id_new_item")
    inputbox.send_keys("Сделать мушку из павлиньих перьев")
    inputbox.send_keys(Keys.ENTER)
    time.sleep(1)
    # Страница снова обновляется, и теперь показывает оба элемента ее списка
    check_for_row_in_list_table("1: Купить павлиньи перья", browser)
    check_for_row_in_list_table("2: Сделать мушку из павлиньих перьев", browser)
    # assert "1: Купить павлиньи перья" in [row.text for row in rows], \
    #     f"Первый элемент списка не появился в таблице. Содержимым было: {table.text}"
    # assert "2: Сделать мушку из павлиньих перьев" in [row.text for row in rows], \
    #     f"Второй элемент списка не появился в таблице. Содержимым было: {table.text}"

    assert False


# Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
# сайт сгенерировал для нее уникальный URL-адрес – об этом
# выводится небольшой текст с объяснениями.

# Она посещает этот URL-адрес – ее список по-прежнему там.

# Удовлетворенная, она снова ложится спать


if __name__ == "__main__":
    sys.exit(pytest.main(["-qq"]))
