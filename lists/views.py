from django.http import HttpResponse
from django.shortcuts import render


def home_page(requets):
    """Домашняя страница"""
    return render(requets, "home.html")
