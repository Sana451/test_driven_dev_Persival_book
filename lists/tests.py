from unittest import TestCase

from django.http import HttpRequest
from django.urls import resolve
from lists.views import home_page


def test_root_url_resolves_to_home_page_view():
    """Тест: корневой url преобразуется в представление домашней страницы"""
    found = resolve("/")
    assert found.func == home_page


def test_home_page_returns_correct_html():
    """Тест: домашняя страница возвращает правильный html"""
    request = HttpRequest()
    response = home_page(request)
    html = response.content.decode('utf8')
    assert html.startswith('<html>') is True
    assert '<title>To-Do lists</title>' in html
    assert html.endswith('</html>') is True
