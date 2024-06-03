from django.http import HttpResponse
from django.shortcuts import render
from django.http.request import HttpRequest


def home_page(requets: HttpRequest):
    """Домашняя страница"""
    return render(requets, "home.html", {"new_item_text": requets.POST.get("item_text", ""), })
