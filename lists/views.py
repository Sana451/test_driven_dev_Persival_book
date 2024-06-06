from django.shortcuts import render, redirect
from django.http.request import HttpRequest

from lists.models import Item, List


def home_page(request: HttpRequest):
    """Домашняя страница"""
    return render(request, "home.html")


def view_list(request: HttpRequest, list_id):
    """Представление списка"""
    list_ = List.objects.get(id=list_id)
    return render(request, "list.html", {'list': list_})


def new_list(request):
    """Новый список"""
    list_ = List.objects.create()
    Item.objects.create(text=request.POST["item_text"], list=list_)
    return redirect(f'/lists/{list_.id}/')


def add_item(request, list_id):
    """Добавить элемент в список"""
    list_ = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST["item_text"], list=list_)

    return redirect(f"/lists/{list_.id}/")
