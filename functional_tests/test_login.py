import sys
import time
import re
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.core import mail
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import (wait_for_row_in_list_table,
                                   browser,
                                   get_item_input_box,
                                   wait_until_presence_of_element)

TEST_EMAIL = "edith@example.com"
SUBJECT = "Superlists login link"


# @pytest.mark.skip
class TestLogin:
    """Тест регистрации в системе."""
    @patch("accounts.views.mail.send_mail")
    def test_can_get_email_link_to_log_in(self, mock_send_mail, browser, live_server):
        """Тест: можно получить ссылку по почте для регистрации."""
        # Эдит заходит на сайт Superlists и впервые
        # замечает раздел "войти" в навигационной панели
        start_url = browser.staging_url if browser.staging_url else live_server.url
        browser.get(start_url)
        browser.find_element(By.NAME, "email").send_keys(TEST_EMAIL)
        browser.find_element(By.NAME, "email").send_keys(Keys.ENTER)
        # появляется сообщение, о том, что ей на почту выслан email
        # wait_until_presence_of_element(browser, '//p[contains(text(), "Check your email")]', By.XPATH)
        wait_until_presence_of_element(browser, '//div[contains(text(), "Check your email")]', By.XPATH)
        # Эдит проверяет свою почту и находит сообщение
        # email = mail.outbox[0]
        _, send_mail_kwargs = mock_send_mail.call_args
        assert TEST_EMAIL in send_mail_kwargs["recipient_list"]
        # assert TEST_EMAIL in email.to
        assert send_mail_kwargs["subject"] == SUBJECT
        # assert email.subject == SUBJECT
        # # Оно содержит ссылку на url-адрес
        assert "Use this link to log in site Superlists:" in send_mail_kwargs["message"]
        # assert "Use this link to log in site Superlists:" in email.body
        url_search = re.search(r'http://.+/.+$', send_mail_kwargs["message"])
        # url_search = re.search(r'http://.+/.+$', email.body)
        if not url_search:
            # pytest.fail(f"Could not find url in email body: '{email.body}'")
            pytest.fail(f"Could not find url in email body: '{send_mail_kwargs['message']}'")
        url = url_search.group(0)
        assert start_url in url
        # Эдит нажимает на ссылку
        browser.get(url)
        # # Она зарегистрирована в системе!
        wait_until_presence_of_element(browser, "Log out", By.LINK_TEXT)
        navbar = browser.find_element(By.CSS_SELECTOR, ".navbar")
        assert TEST_EMAIL in navbar.text

        # выход и повторный вход
        # browser.find_element(By.LINK_TEXT, "Log out").click()
        # wait_until_presence_of_element(browser, "email", By.NAME)
        # browser.find_element(By.NAME, "email").send_keys(TEST_EMAIL)
        # browser.find_element(By.NAME, "email").send_keys(Keys.ENTER)
        # wait_until_presence_of_element(browser, "a[href]", By.CSS_SELECTOR)
        # browser.find_element(By.CSS_SELECTOR, "a[href]").click()
        # wait_until_presence_of_element(browser, "Log out", By.LINK_TEXT)
