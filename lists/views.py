from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http.request import HttpRequest

from functional_tests.base import DUPLICATE_ITEM_ERROR
from lists.forms import ItemForm
from lists.models import List


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
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, "home.html", {"form": form})
