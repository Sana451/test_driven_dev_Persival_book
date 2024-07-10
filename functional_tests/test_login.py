import os
import re
import datetime
import time

from django.conf import settings
from imap_tools import MailBox, AND
from django.test import override_settings
import pytest
from unittest.mock import patch
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import (browser,
                                   wait_until_presence_of_element)

TEST_EMAIL = "sana451@mail.ru"
SUBJECT = "Superlists login link"


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
        wait_until_presence_of_element(browser, '//div[contains(text(), "Check your email")]', By.XPATH)
        # Эдит проверяет свою почту и находит сообщение
        _, send_mail_kwargs = mock_send_mail.call_args
        assert TEST_EMAIL in send_mail_kwargs["recipient_list"]
        assert send_mail_kwargs["subject"] == SUBJECT
        # Оно содержит ссылку на url-адрес
        assert "Use this link to log in site Superlists:" in send_mail_kwargs["message"]
        url_search = re.search(r'http://.+/.+$', send_mail_kwargs["message"])
        if not url_search:
            pytest.fail(f"Could not find url in email body: '{send_mail_kwargs['message']}'")
        url = url_search.group(0)
        assert start_url in url
        # Эдит нажимает на ссылку
        browser.get(url)
        # Она зарегистрирована в системе!
        wait_until_presence_of_element(browser, "//button[text()='Log out']", By.XPATH)
        navbar = browser.find_element(By.CSS_SELECTOR, ".navbar")
        assert TEST_EMAIL in navbar.text
        # Теперь она выходит из системы
        browser.find_element(By.XPATH, "//button[text()='Log out']").click()
        # Она вышла из системы
        wait_until_presence_of_element(browser, "email", By.NAME)
        navbar = browser.find_element(By.CSS_SELECTOR, ".navbar")
        assert TEST_EMAIL not in navbar.text

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_can_send_real_email(self, browser, live_server):
        """Тест: отправляются настоящие email."""
        # Эдит заходит на сайт Superlists, вводит email
        start_url = browser.staging_url if browser.staging_url else live_server.url
        browser.get(start_url)
        print(settings.EMAIL_BACKEND)
        browser.find_element(By.NAME, "email").send_keys(TEST_EMAIL)
        browser.find_element(By.NAME, "email").send_keys(Keys.ENTER)
        wait_until_presence_of_element(browser, '//div[contains(text(), "Check your email")]', By.XPATH)
        # Эдит проверяет свою почту и находит сообщение
        last_message = None
        with MailBox("imap.mail.ru").login(username=TEST_EMAIL,
                                           password=os.environ.get("EMAIL_INCOMING_PASSWORD_FOR_TEST")
                                           ) as mailbox:
            while last_message is None:
                time.sleep(5)
                messages = list(mailbox.fetch(
                    AND(subject=SUBJECT, date=datetime.date.today()))
                )
                if not messages:
                    print(f"Empty messages list with subject {SUBJECT}")
                for msg in list(messages):
                    url_search = re.search(r'http://.+/.+$', msg.text)
                    url = url_search.group(0)
                    if url.startswith(start_url) is True:
                        last_message = msg
            mailbox.delete([msg.uid])

        # Эдит нажимает на ссылку в этом сообщении
        browser.get(url)
        # Она зарегистрирована в системе!
        wait_until_presence_of_element(browser, "//button[text()='Log out']", By.XPATH)
        navbar = browser.find_element(By.CSS_SELECTOR, ".navbar")
        assert TEST_EMAIL in navbar.text
