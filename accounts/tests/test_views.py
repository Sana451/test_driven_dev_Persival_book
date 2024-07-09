import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects
import accounts.views
from unittest.mock import patch, call

from accounts.models import Token


@pytest.mark.django_db
class TestSendLoginEmailView:
    """Тест представления, которое отправляет сообщение для входа в систему."""

    def test_redirects_to_home_page(self, client: Client):
        """Тест: переадресация на домашнюю страницу."""
        response = client.post("/accounts/send_login_email", data={"email": "edith@example.com"})

        assertRedirects(response, "/")

    def test_sends_mail_to_address_from_post(self, client: Client):
        """Тест: отправляется сообщение на адрес из метода post."""
        self.send_mail_called = False

        def fake_send_mail(subject, message, from_email, recipient_list, **kwargs):
            """Поддельная функция send_mail."""
            self.send_mail_called = True
            self.subject = subject
            self.message = message
            self.from_email = from_email
            self.recipient_list = recipient_list

        accounts.views.mail.send_mail = fake_send_mail
        client.post("/accounts/send_login_email", data={"email": "edith@example.com"})  # выполнить views.send_mail

        assert self.send_mail_called is True
        assert self.subject == "Superlists login link"
        assert self.from_email == "superlists@admin.com"
        assert self.recipient_list == ["edith@example.com"]

    @patch("accounts.views.mail.send_mail")
    def test_sends_mail_to_address_from_post_with_mock(self, mock_send_mail, client: Client):
        client.post("/accounts/send_login_email", data={"email": "edith@example.com"})
        (subject, message, from_email, recipient_list, *kwargs) = mock_send_mail.call_args[1].values()

        assert mock_send_mail.called is True
        assert subject == "Superlists login link"
        assert from_email == "superlists@admin.com"
        assert recipient_list == ["edith@example.com"]

    @patch("accounts.views.messages")
    def test_adds_success_message_with_mocks(self, mock_messages, client: Client):
        """Тест: добавляется сообщение об успехе."""
        response = client.post("/accounts/send_login_email", data={"email": "edith@example.com"})
        expected = "Check your email, you'll find a message with a link that will log you into the site."
        _, mock_message_kwargs = mock_messages.success.call_args
        assert mock_message_kwargs["request"] == response.wsgi_request
        assert mock_message_kwargs["message"] == expected


@patch("accounts.views.auth")
@pytest.mark.django_db
class TestLoginView:
    """Тест представления входа в систему."""

    def test_redirects_to_home_page(self, mock_auth_module, client: Client):
        """Тест: переадресуется на домашнюю страницу."""
        response = client.get("/accounts/login?uid=abcd123")

        assertRedirects(response, "/")

    def test_creates_token_associated_with_email(self, mock_auth_module, client: Client):
        """Тест: создается маркер, связанный с электронной почтой."""
        client.post("/accounts/send_login_email", data={"email": "edith@example.com"})
        token = Token.objects.first()

        assert token.email == "edith@example.com"

    @patch("accounts.views.mail.send_mail")
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail_func, mock_auth_module, client: Client):
        """Тест: отсылается ссылка на вход в систему, используя uid маркера."""
        client.post("/accounts/send_login_email", data={"email": "edith@example.com"})
        token = Token.objects.first()
        expected_url = f"http://testserver/accounts/login?uid={token.uid}"
        subject, message, from_email, recipient_list, *kwargs = mock_send_mail_func.call_args[1].values()

        assert expected_url in message

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth_module, client: Client):
        """Тест: вызывается authenticate с uid из GET-запроса."""
        client.get("/accounts/login?uid=abcd123")

        assert mock_auth_module.authenticate.call_args == call(uid="abcd123")

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth_module, client: Client):
        """Тест: вызывается auth_login с пользователем, если такой имеется."""
        response = client.get("/accounts/login?uid=abcd123")

        assert mock_auth_module.login.call_args == call(response.wsgi_request,
                                                        mock_auth_module.authenticate.return_value)

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth_module, client: Client):
        """Тест: не регистрируется в системе, если пользователь не аутентифицирован."""
        mock_auth_module.authenticate.return_value = None
        client.get("/accounts/login?token=abcd123")
        assert mock_auth_module.login.called is False
