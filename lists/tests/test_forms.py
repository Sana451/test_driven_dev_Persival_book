from lists.forms import ItemForm, EMPTY_ITEM_ERROR


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
