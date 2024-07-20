import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client
from django.utils.html import escape
from pytest_django.asserts import assertTemplateUsed, assertRedirects
from rest_framework import status

from lists.forms import ItemForm, EMPTY_ITEM_ERROR
from lists.models import Item, List

User = get_user_model()


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

        client.post(f"/lists/{correct_list.id}/", data={"text": "A new item for an existing list"})

        assert Item.objects.count() == 1
        new_item = Item.objects.first()
        assert new_item.text == "A new item for an existing list"
        assert new_item.list == correct_list

    def test_POST_redirects_to_list_view(self, client: Client):
        """Тест: переадресуется в представление списка"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = client.post(f"/lists/{correct_list.id}/", data={"text": "A new item for an existing list"})

        assertRedirects(response, f"/lists/{correct_list.id}/")

    def post_invalid_input(self, client: Client):
        """Вспомогательная функция для отправки недопустимого ввода."""
        list_ = List.objects.create()
        return client.post(f"/lists/{list_.id}/", data={"text": ""})

    def test_for_invalid_input_nothing_saved_to_db(self, client: Client):
        """Тест на недопустимый ввод: ничего не сохраняется в БД."""
        self.post_invalid_input(client)
        assert Item.objects.count() == 0

    def test_valid_input_saved_to_db(self, client: Client):
        """Тест на недопустимый ввод: ничего не сохраняется в БД."""
        list_ = List.objects.create()
        client.post(f"/lists/{list_.id}/", data={"text": "Save first text to database"})
        client.post(f"/lists/{list_.id}/", data={"text": "Save second text to database"})
        assert Item.objects.count() == 2
        assert Item.objects.last().text == "Save second text to database"

    def test_for_invalid_input_renders_list_template(self, client: Client):
        """Тест на недопустимый ввод: отображается шаблон списка."""
        response = self.post_invalid_input(client)
        assert response.status_code == status.HTTP_200_OK
        assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_passes_form_to_template(self, client: Client):
        """Тест на недопустимый ввод: форма передается в шаблон."""
        response = self.post_invalid_input(client)
        assert isinstance(response.context["form"], ItemForm)

    def test_for_invalid_input_shows_error_on_page(self, client: Client):
        """Тест на недопустимый ввод: на странице показывается ошибка."""
        response = self.post_invalid_input(client)
        assert escape(EMPTY_ITEM_ERROR) in response.content.decode()

    def test_displays_item_form(self, client: Client):
        """Тест отображения формы для элемента."""
        list_ = List.objects.create()
        response = client.get(f"/lists/{list_.id}/")
        assert isinstance(response.context["form"], ItemForm)
        assert 'name="text"' in response.content.decode()


@pytest.mark.django_db
class TestNewList:
    """Тест нового списка."""

    def test_can_save_a_POST_request(self, client: Client):
        """Тест: можно сохранить post-запрос."""
        response = client.post("/lists/new", data={"text": "A new list item"})
        assert response.status_code == status.HTTP_302_FOUND
        assert Item.objects.count() == 1
        new_item = Item.objects.first()
        assert new_item.text == "A new list item"

    def test_redirects_after_POST(self, client: Client):
        """Тест: переадресует после post-запроса"""
        response = client.post("/lists/new", data={'text': "A new list item"})
        new_list = List.objects.first()

        assertRedirects(response, f"/lists/{new_list.id}/")

    def test_for_invalid_input_renders_home_template(self, client: Client):
        """Тест на недопустимый ввод: отображает домашний шаблон."""
        response: HttpResponse = client.post("/lists/new", data={"text": ""})
        assert response.status_code == status.HTTP_200_OK
        assertTemplateUsed(response, "home.html")

    def test_validation_errors_are_shown_on_home_page(self, client: Client):
        """Тест: ошибки валидации выводятся на домашней странице."""
        response: HttpResponse = client.post("/lists/new", data={"text": ""})
        expected_error = escape(EMPTY_ITEM_ERROR)
        assert expected_error in response.content.decode()

    def test_for_invalid_input_passes_form_to_template(self, client: Client):
        """Тест на недопустимый ввод: форма передается в шаблон."""
        response: HttpResponse = client.post("/lists/new", data={"text": ""})
        assert isinstance(response.context["form"], ItemForm)

    def test_invalid_list_items_arent_saved(self, client: Client):
        """Тест: сохраняются недопустимые элементы списка."""
        client.post("/lists/new", data={"text": ""})
        assert List.objects.count() == 0
        assert Item.objects.count() == 0

    def test_list_owner_is_saved_if_user_is_authenticated(self, client: Client):
        """Тест: владелец сохраняется, если пользователь аутентифицирован."""
        user = User.objects.create(email='a@b.com')
        client.force_login(user)
        client.post("/lists/new", data={"text": "new item"})
        list_ = List.objects.first()
        assert list_.owner == user


class TestHomePage:
    """Тест домашней страницы."""

    def test_uses_home_template(self, client: Client):
        """Тест: использует домашний шаблон."""
        response = client.get("")
        assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self, client: Client):
        """Тест: домашняя страница использует форму для элемента."""
        response = client.get("")
        assert isinstance(response.context["form"], ItemForm)


@pytest.mark.django_db
class TestMyLists:
    """Тест сохранения моих списков."""

    def test_my_lists_url_renders_my_lists_template(self, client: Client):
        User.objects.create(email="a@b.com")
        response = client.get("/lists/users/a@b.com/")
        assertTemplateUsed(response, "my_lists.html")

    def test_passes_correct_owner_to_template(self, client):
        """Тест: передается правильный владелец в шаблон."""
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = client.get("/lists/users/a@b.com/")
        assert response.context["owner"] == correct_user


@pytest.mark.django_db
class TestSharedList:
    """Тест совместного использования списков."""

    def test_post_redirects_to_lists_page(self, client: Client):
        """Тест: POST-запрос переадресуется на страницу списка."""
        list_ = List.objects.create()
        item = Item.objects.create(text="List 1", list=list_)
        response = client.post(f"/lists/{list_.pk}/share/", data={"email": "user@email.ru"})
        assertRedirects(response, list_.get_absolute_url())

    def test_can_add_user_to_list_shared_with(self, client: Client):
        """Тест: пользователю добавлен доступ к просмотру списка."""
        user = User.objects.create(email="test_user@mail.ru")
        list_ = List.objects.create()
        client.post(f"/lists/{list_.pk}/share/", data={"email": user.email})
        assert user in list_.shared_with.all()
