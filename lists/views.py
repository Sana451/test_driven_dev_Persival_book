from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.views.decorators.http import require_POST

from functional_tests.base import DUPLICATE_ITEM_ERROR
from lists.forms import ItemForm
from lists.models import List

User = get_user_model()


def home_page(request: HttpRequest):
    """Домашняя страница."""
    return render(request, "home.html", context={"form": ItemForm()})


def view_list(request: HttpRequest, list_id):
    """Представление списка."""
    list_ = List.objects.get(id=list_id)
    form = ItemForm()
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                form.save(for_list=list_)
                return redirect(list_)
            except IntegrityError:
                form.errors["text"] = DUPLICATE_ITEM_ERROR
    return render(request, "list.html", {"list": list_, "form": form})


def new_list(request):
    """Новый список."""
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
        if request.user.is_authenticated:
            list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, "home.html", {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, "my_lists.html", context={"owner": owner})


@require_POST
def share_list(request: HttpRequest, list_id):
    email = request.POST["email"]
    user = User.objects.get_or_create(email=email)[0]
    list_ = List.objects.get(pk=list_id)
    list_.shared_with.add(user)
    return redirect(list_)
