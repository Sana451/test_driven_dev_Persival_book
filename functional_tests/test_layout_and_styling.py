import math

from pytest_django.fixtures import live_server
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import wait_for_row_in_list_table, browser, get_item_input_box


class TestLayoutAndStyling:
    """Тест макета и стилевого оформления."""

    def test_layout_and_styling(self, browser, live_server):
        """Тест макета и стилевого оформления"""
        # Эдит открывает домашнюю страницу
        staging_url = browser.staging_url
        browser.get(staging_url if staging_url else live_server.url)
        browser.set_window_size(1024, 768)
        # Она замечает, что поле ввода аккуратно центрировано
        input_box = get_item_input_box(browser)

        related_tolerance = 0.06
        assert math.isclose(
            a := 512,
            b := input_box.location["x"] + input_box.size["width"] / 2,
            rel_tol=related_tolerance
        ), f"{a} != {b}, within {a * related_tolerance} delta"

        # # заголовок теперь имеет красный цвет (rgba 255, 0, 0, 1), похоже, что base.css загружен
        h1_to_do_title = browser.find_element(By.CSS_SELECTOR, ".text-center h1")
        h1_color = h1_to_do_title.value_of_css_property("color")
        assert h1_color == "rgba(255, 0, 0, 1)"

        # Она начинает новый список и видит, что поле ввода там
        # также находится по центру
        input_box.send_keys("testing")
        input_box.send_keys(Keys.ENTER)
        wait_for_row_in_list_table("1: testing", browser)

        input_box = get_item_input_box(browser)

        assert math.isclose(
            a := 512,
            b := input_box.location["x"] + input_box.size["width"] / 2,
            rel_tol=related_tolerance
        ), f"{a} != {b}, within {a * related_tolerance} delta"
