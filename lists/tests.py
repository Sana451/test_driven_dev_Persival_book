from unittest import TestCase
from django.urls import resolve
from lists.views import home_page


def test_root_url_resolves_to_home_page_view():
    """Тест: корневой url преобразуется в представление домашней страницы"""
    found = resolve("/")
    assert found.func == home_page
