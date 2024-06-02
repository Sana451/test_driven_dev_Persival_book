from django.http import HttpResponse
from django.shortcuts import render


def home_page(requets):
    """Домашняя страница"""
    return HttpResponse("<html><title>To-Do lists</title><p>To do</p></html>")
