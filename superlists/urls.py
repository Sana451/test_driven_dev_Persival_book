from django.contrib import admin
from django.urls import path, include, re_path
from lists import views
from lists import urls as list_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home_page, name="home"),

    re_path("^lists/", include(list_urls)),
]