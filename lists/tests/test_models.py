import pytest
from django.core.exceptions import ValidationError

from lists.models import Item, List


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
        assert saved_items[0].text == "The first (ever) list item"
        assert saved_items[1].list == list_
        assert saved_items[1].text == "Item the second"
        assert saved_items[1].list == list_

    def test_cannot_save_empty_list_items(self):
        """Тест: нельзя добавлять пустые элементы списка."""
        list_ = List.objects.create()
        item = Item(text="", list=list_)
        with pytest.raises(ValidationError):
            item.save()
            item.full_clean()
