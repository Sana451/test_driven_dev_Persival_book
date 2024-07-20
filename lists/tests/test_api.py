import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
# from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR

from rest_framework import status
from lists.models import List, Item

User = get_user_model()

base_url = "/api/lists/{}/"


def post_empty_input(client: Client):
    list_ = List.objects.create()
    return client.post(base_url.format(list_.id), data={"text": ""})


@pytest.mark.django_db
class TestListAPI:
    """Тест API списков."""

    def test_get_returns_json_200(self, client: Client):
        """Тест: возвращает json и код состояния 200."""
        list_ = List.objects.create()
        response = client.get(base_url.format(list_.id))

        assert response.status_code == status.HTTP_200_OK
        assert response["content-type"] == "application/json"

    def test_get_returns_items_for_correct_list(self, client: Client):
        """Тест: получает отклик с элементами правильного списка."""
        other_list = List.objects.create()
        Item.objects.create(text="Item for other list", list=other_list)
        our_list = List.objects.create()
        item1 = Item.objects.create(text="Item 1 for our list", list=our_list)
        item2 = Item.objects.create(text="Item 2 for our list", list=our_list)
        response = client.get(base_url.format(our_list.id))

        assert json.loads(response.content.decode("utf8")) == [
            {'id': item1.id, 'text': item1.text},
            {'id': item2.id, 'text': item2.text},
        ]

    def test_POSTing_a_new_item(self, client: Client):
        """Тест: POST запрос создаёт новый элемент списка."""
        list_ = List.objects.create()
        response = client.post(base_url.format(list_.id), data={"text": "new item with POST"})
        item = list_.item_set.get()

        assert response.status_code == status.HTTP_201_CREATED
        assert item.text == "new item with POST"

    def test_for_invalid_input_nothing_saved_to_db(self, client: Client):
        """Тест: пустой POST запрос не сохраняет в БД."""
        assert Item.objects.count() == 0
        post_empty_input(client)
        assert Item.objects.count() == 0
