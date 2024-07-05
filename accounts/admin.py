from django.contrib import admin

from accounts.models import Token, ListUser

admin.site.register(Token)
admin.site.register(ListUser)
