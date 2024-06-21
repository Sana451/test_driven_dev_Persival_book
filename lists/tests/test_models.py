import pytest

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

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        assert first_saved_item.text == "The first (ever) list item"
        assert first_saved_item.list == list_
        assert second_saved_item.text == "Item the second"
        assert second_saved_item.list == list_
