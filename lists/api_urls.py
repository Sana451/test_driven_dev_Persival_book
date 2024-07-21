from django.urls import re_path
from lists import api

urlpatterns = [
    re_path(r"^lists/(\d+)/$", api.item_api, name="api_list"),
]
