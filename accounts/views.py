import sys
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.http import HttpRequest
from django.shortcuts import render, redirect
from accounts.models import Token


def send_login_email(request: HttpRequest):
    """Выслать ссылку на логин по почте."""
    email = request.POST["email"]
    uid = str(uuid.uuid4())
    Token.objects.create(email=email, uid=uid)
    print('saving uid', uid, 'for email', email, file=sys.stderr)
    url = request.build_absolute_uri(f"/accounts/login?uid={uid}")
    send_mail(
        subject="Superlists login link",
        message=f"Use this link to log in site Superlists: \n\n{url}",
        from_email="superlists@admin.com",
        recipient_list=[email],
        fail_silently=False,
    )
    # WARNING delete url from context before use in PRODUCTION (use not console EMAIL_BACKEND in settings.py)
    return render(request, "login_email_sent.html", {"url": url})


def login(request):
    """Регистрация в системе."""
    print("run login view", file=sys.stderr)
    uid = request.GET.get('uid')
    user = authenticate(uid=uid)
    if user is not None:
        auth_login(request, user)
    return redirect('/')


def logout(request):
    """Выход из системы."""
    auth_logout(request)
    return redirect('/')