import math

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import wait_for_row_in_list_table, browser


class TestLayoutAndStyling:
    """Тест макета и стилевого оформления."""

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


