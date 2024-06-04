from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http.request import HttpRequest

from lists.models import Item


def home_page(requets: HttpRequest):
    """Домашняя страница"""
    if requets.method == "POST":
        new_item_text = requets.POST['item_text']
        Item.objects.create(text=new_item_text)
        return redirect('/')

    items = Item.objects.all()
    return render(requets, "home.html", {'items': items})
