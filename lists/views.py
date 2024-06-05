from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http.request import HttpRequest

from lists.models import Item


def home_page(request: HttpRequest):
    """Домашняя страница"""
    return render(request, "home.html")


def view_list(request: HttpRequest):
    """Представление списка"""
    items = Item.objects.all()
    return render(request, "list.html", {'items': items})


def new_list(request):
    """Новый список"""
    Item.objects.create(text=request.POST["item_text"])
    return redirect('/lists/url-for-redirect/')
