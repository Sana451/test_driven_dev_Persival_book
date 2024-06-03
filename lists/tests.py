from django.http import HttpRequest
from django.urls import resolve
from django.template.loader import render_to_string

from lists.views import home_page


def test_home_page_returns_correct_html(client):
    """Тест: домашняя страница возвращает правильный html"""
    response = client.get("/")
    html = response.content.decode('utf8')
    expected_html = render_to_string("home.html")
    assert html == expected_html
