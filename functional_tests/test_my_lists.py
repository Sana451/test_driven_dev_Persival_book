import re
import time

import pytest
from unittest.mock import patch
from django.conf import settings
from pytest_django.fixtures import live_server
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import (browser,
                                   wait_until_presence_of_element)

User = get_user_model()


@pytest.mark.django_db
class TestMyLists:
    """Тест приложения “Мои списки”."""

    def create_pre_authenticated_session(self, email, browser, live_server):
        """Создать предварительно аутентифицированный сеанс."""
        user = User.objects.create(email=email)
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        ## установить cookie, которые нужны для первого посещения домена.
        ## страницы 404 загружаются быстрее всего!
        start_url = browser.staging_url if browser.staging_url else live_server.url
        browser.get(start_url + "/404_no_such_url/")
        browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path="/",
        ))

    def test_logged_in_users_lists_are_saved_as_my_lists(self, browser, live_server):
        """Тест: списки зарегистрированных пользователей сохраняются как «мои списки»"""
        start_url = browser.staging_url if browser.staging_url else live_server.url
        email = "edith@example.com"
        browser.get(start_url)
        wait_until_presence_of_element(browser, "email", By.NAME)
        # Эдит является зарегистрированным пользователем
        self.create_pre_authenticated_session(email, browser, live_server)
        browser.get(start_url)
        wait_until_presence_of_element(browser, "//button[text()='Log out']", By.XPATH)


# def wait_to_be_logged_in(self, email):
# '''ожидать входа в систему'''
# self.wait_for(
# lambda: self.browser.find_element_by_link_text('Log out')
# )
# navbar = self.browser.find_element_by_css_selector('.navbar')Пропуск регистрации в системе путем предварительного создания сеанса  403
# self.assertIn(email, navbar.text)

# def wait_to_be_logged_out(self, email):
# '''ожидать выхода из системы'''
# self.wait_for(
# lambda: self.browser.find_element_by_name('email')
# )
# navbar = self.browser.find_element_by_csr('.navbar')