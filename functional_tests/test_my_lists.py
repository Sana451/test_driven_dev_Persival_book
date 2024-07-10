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
                                   wait_until_presence_of_element,
                                   add_list_item)

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
        """Тест: списки зарегистрированных пользователей сохраняются как «мои списки»."""
        start_url = browser.staging_url if browser.staging_url else live_server.url
        email = "edith@example.com"
        browser.get(start_url)
        wait_until_presence_of_element(browser, "email", By.NAME)
        # Эдит является зарегистрированным пользователем
        self.create_pre_authenticated_session(email, browser, live_server)
        browser.get(start_url)
        wait_until_presence_of_element(browser, "//button[text()='Log out']", By.XPATH)
        # Эдит начинает новый список
        add_list_item("Reticulate splines", browser)
        add_list_item("Immanentize eschaton", browser)
        first_list_url = browser.current_url
        # Она замечает ссылку на "Мои списки" в первый раз.
        browser.find_element(By.LINK_TEXT, "My lists").click()
        # Она видит, что ее список находится там, и он назван
        # на основе первого элемента списка
        wait_until_presence_of_element(browser, "Reticulate splines", By.LINK_TEXT)
        wait_until_presence_of_element(browser, "Reticulate splines", By.LINK_TEXT)

        self.browser.find_element_by_link_text('Reticulate splines').click()
        assert browser.current_url == first_list_url
        # Она решает начать еще один список, чтобы только убедиться
        browser.get(live_server.url)
        add_list_item("Click cows", browser)
        second_list_url = browser.current_url
        # Под заголовком "Мои списки" появляется ее новый список
        browser.find_element(By.LINK_TEXT, "My lists").click()
        wait_until_presence_of_element(browser, "Click cows", By.LINK_TEXT)
        browser.find_element(By.LINK_TEXT, "Click cows").click()
        assert browser.current_url == second_list_url
        # Она выходит из системы. Опция "Мои списки" исчезает
        browser.find_element(By.XPATH, "//button[text()='Log out']").click()
        assert browser.find_element(By.LINK_TEXT, "My lists") == []
