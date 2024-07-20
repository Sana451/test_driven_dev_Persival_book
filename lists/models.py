from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class List(models.Model):
    """Список дел"""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name="my_list")

    @property
    def name(self):
        """Имя."""
        return self.item_set.first().text

    def get_absolute_url(self):
        """Получить абсолютный url"""
        return reverse("view_list", args=[self.id])


class Item(models.Model):
    """Элемент списка"""
    text = models.TextField(default=None, blank=False)
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')
