from django.http import HttpRequest
from django.urls import resolve
from django.template.loader import render_to_string
from django.test import Client
from pytest_django.asserts import assertTemplateUsed

from lists.views import home_page


def test_home_page_returns_correct_html(client: Client):
    """Тест: домашняя страница возвращает правильный html"""
    response = client.get("/")
    assertTemplateUsed(response, "home.html")


def test_can_save_a_POST_request(client: Client):
    """Тест: можно сохранить post-запрос"""
    response = client.post("/", data={'item_text': 'A new list item'})
    assert 'A new list item' in response.content.decode()
    assertTemplateUsed(response, 'home.html')
