import pytest
from django.core.exceptions import ValidationError

from lists.models import Item, List


@pytest.mark.django_db
class TestItemModel:
    """Тест модели элемента."""

    def test_default_text(self):
        """Тест заданного по умолчанию текста."""
        item = Item()
        assert item.text == ""

    def test_string_representation(self):
        """Тест строкового представления."""
        item = Item(text="some text")
        assert str(item) == "some text"


@pytest.mark.django_db
class TestListModel:
    """Тест модели списка."""

    def test_get_absolute_url(self):
        """Тест: получен абсолютный url."""
        list_ = List.objects.create()
        assert list_.get_absolute_url() == f"/lists/{list_.id}/"

    def test_list_ordering(self):
        """Тест упорядочения списка."""
        list_1 = List.objects.create()
        item_1 = Item.objects.create(list=list_1, text="i1")
        item_2 = Item.objects.create(list=list_1, text="item 2")
        item_3 = Item.objects.create(list=list_1, text="3")
        assert list(Item.objects.all()) == [item_1, item_2, item_3]


@pytest.mark.django_db
class TestListAndItemModels:
    """Тест моделей списка и элемента."""

    def test_item_is_related_to_list(self):
        """Тест: элемент связан со списком."""
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        assert item in list_.item_set.all()

    def test_duplicate_items_are_invalid(self):
        """Тест: повторы элементов не допустимы."""
        list_ = List.objects.create()
        Item.objects.create(list=list_, text="bla")
        with pytest.raises(ValidationError):
            item = Item(list=list_, text="bla")
            item.full_clean()

    def test_CAN_save_same_item_to_different_lists(self):
        """Тест: МОЖЕТ сохранить тот же элемент в разные списки."""
        list_1 = List.objects.create()
        list_2 = List.objects.create()
        Item.objects.create(list=list_1, text="bla")
        item = Item.objects.create(list=list_2, text="bla")
        item.full_clean()  # не должен поднять исключение
