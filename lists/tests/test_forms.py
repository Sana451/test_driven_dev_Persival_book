import pytest

from lists.forms import ItemForm, EMPTY_ITEM_ERROR
from lists.models import List, Item


class TestItemForm:
    """Тест формы для элемента списка."""

    def test_form_renders_item_text_input(self):
        """Тест: форма отображает текстовое поле ввода."""
        form = ItemForm()
        assert 'placeholder="Enter a to-do item"' in form.as_p()
        assert 'class="form-control input-lg"' in form.as_p()

    def test_form_validation_for_blank_items(self):
        """Тест валидации формы для пустых элементов."""
        form = ItemForm(data={"text": ""})
        assert form.is_valid() is False
        assert form.errors["text"][0] == EMPTY_ITEM_ERROR

    @pytest.mark.django_db
    def test_form_save_handles_saving_to_a_list(self):
        """Тест: метод save формы обрабатывает сохранение в список."""
        list_ = List.objects.create()
        form = ItemForm(data={"text": "do me"})
        new_item = form.save(for_list=list_)
        # new_item = form.save(commit=False)
        # new_item.list = list_
        # new_item.save()
        assert new_item == Item.objects.first()
        assert new_item.text == "do me"
        assert new_item.list == list_
