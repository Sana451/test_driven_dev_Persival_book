import pytest
from django.http import HttpResponse
from django.test import Client
from django.utils.html import escape
from pytest_django.asserts import assertTemplateUsed, assertRedirects
from rest_framework import status

from lists.models import Item, List


@pytest.mark.django_db
def test_home_page_returns_correct_html(client: Client):
    """Тест: домашняя страница возвращает правильный html"""
    response = client.get("/")
    assertTemplateUsed(response, "home.html")


@pytest.mark.django_db
class TestListView:
    """Тест представления списка."""

    def test_uses_list_template(self, client: Client):
        """Тест: используется шаблон списка."""
        list_ = List.objects.create()
        response = client.get(f"/lists/{list_.id}/")

        assertTemplateUsed(response, "list.html")

    def test_displays_only_items_for_that_list(self, client: Client):
        """Тест: отображаются элементы только для этого списка"""
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='другой элемент 1 списка', list=other_list)
        Item.objects.create(text='другой элемент 2 списка', list=other_list)

        response = client.get(f'/lists/{correct_list.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert 'itemey 1' in response.content.decode()
        assert 'itemey 2' in response.content.decode()
        assert 'другой элемент 1 списка' not in response.content.decode()
        assert 'другой элемент 2 списка' not in response.content.decode()

    def test_passes_correct_list_to_template(self, client: Client):
        """Тест: передается правильный шаблон списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = client.get(f"/lists/{correct_list.id}/")

        assert response.context["list"] == correct_list

    def test_can_save_a_POST_request_to_an_existing_list(self, client: Client):
        """Тест: можно сохранить post-запрос в существующий список"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        client.post(f"/lists/{correct_list.id}/", data={"item_text": "A new item for an existing list"})

        assert Item.objects.count() == 1
        new_item = Item.objects.first()
        assert new_item.text == "A new item for an existing list"
        assert new_item.list == correct_list

    def test_POST_redirects_to_list_view(self, client: Client):
        """Тест: переадресуется в представление списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = client.post(f"/lists/{correct_list.id}/", data={"item_text": "New item 4 existing lst"})

        assertRedirects(response, f"/lists/{correct_list.id}/")


@pytest.mark.django_db
class TestNewList:
    """Тест нового списка."""

    def test_can_save_a_POST_request(self, client: Client):
        """Тест: можно сохранить post-запрос."""
        response = client.post("/lists/new", data={"item_text": "A new list item"})
        assert response.status_code == status.HTTP_302_FOUND
        assert Item.objects.count() == 1
        new_item = Item.objects.first()
        assert new_item.text == "A new list item"

    def test_redirects_after_POST(self, client: Client):
        """Тест: переадресует после post-запроса"""
        response = client.post("/lists/new", data={'item_text': "A new list item"})
        new_list = List.objects.first()

        assertRedirects(response, f"/lists/{new_list.id}/")

    def test_validation_errors_are_sent_back_to_home_page_template(self, client: Client):
        """Тест: ошибки валидации отсылаются назад в шаблон домашней страницы."""
        response: HttpResponse = client.post("/lists/new", data={"item_text": ""})
        assert response.status_code == status.HTTP_200_OK
        assertTemplateUsed(response, "home.html")
        expected_error = escape("You can't have an empty list item")
        assert expected_error in response.content.decode()

    def test_invalid_list_items_arent_saved(self, client: Client):
        """Тест: сохраняются недопустимые элементы списка."""
        client.post("/lists/new", data={"item_text": ""})
        assert List.objects.count() == 0
        assert Item.objects.count() == 0
