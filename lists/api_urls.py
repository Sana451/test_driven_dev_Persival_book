from django.urls import re_path
from lists import views, api

urlpatterns = [
    re_path(r"^lists/(\d+)/$", api.list_api, name="api_list"),
]
