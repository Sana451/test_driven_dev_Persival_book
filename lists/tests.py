import pytest
from django.test import Client
from pytest_django.asserts import assertTemplateUsed, assertRedirects
from rest_framework import status

from lists.models import Item, List


@pytest.mark.django_db
def test_home_page_returns_correct_html(client: Client):
    """Тест: домашняя страница возвращает правильный html"""
    response = client.get("/")
    assertTemplateUsed(response, "home.html")


@pytest.mark.django_db
class TestListAndItemModels:
    def test_saving_and_retrieving_items(self):
        """Тест сохранения и получения элементов списка"""
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = "The first (ever) list item"
        first_item.list = list_
        first_item.save()
        second_item = Item()
        second_item.text = "Item the second"
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        assert saved_list == list_

        saved_items = Item.objects.all()
        assert saved_items.count() == 2

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        assert first_saved_item.text == "The first (ever) list item"
        assert first_saved_item.list == list_
        assert second_saved_item.text == "Item the second"
        assert second_saved_item.list == list_


@pytest.mark.django_db
def test_uses_list_template(client: Client):
    """Тест: используется шаблон списка"""
    response = client.get('/lists/url-for-redirect/')

    assertTemplateUsed(response, "list.html")


@pytest.mark.django_db
def test_displays_all_items(client: Client):
    """Тест представления списка"""
    list_ = List.objects.create()
    Item.objects.create(text='itemey 1', list=list_)
    Item.objects.create(text='itemey 2', list=list_)

    response = client.get('/lists/url-for-redirect/')

    assert response.status_code == status.HTTP_200_OK
    assert 'itemey 1' in response.content.decode()
    assert 'itemey 2' in response.content.decode()


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

        assertRedirects(response, "/lists/url-for-redirect/")
