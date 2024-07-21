import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from rest_framework import routers, serializers, viewsets
from rest_framework.validators import UniqueTogetherValidator

from functional_tests.base import DUPLICATE_ITEM_ERROR
from lists.forms import EMPTY_ITEM_ERROR
from lists.models import List, Item


def item_api(request, list_id):
    list_ = List.objects.get(pk=list_id)

    if request.method == "GET":
        item_dicts = [{"id": item.id, "text": item.text} for item in list_.item_set.all()]
        return HttpResponse(json.dumps(item_dicts), content_type="application/json")

    elif request.method == "POST":
        try:
            item = Item(text=request.POST.get("text"), list=list_)
            item.full_clean()
            item.save()
            return JsonResponse(data={"item": item.text}, status=201)
        except ValidationError:
            list_.delete()
            return JsonResponse(data={"error": "You can't have an empty list item"}, status=400)


class ItemSerializer(serializers.ModelSerializer):
    text = serializers.CharField(allow_blank=False, error_messages={'blank': EMPTY_ITEM_ERROR})

    class Meta:
        model = Item
        fields = ('id', 'list', 'text')
        validators = [
            UniqueTogetherValidator(
                queryset=Item.objects.all(),
                fields=('list', 'text'),
                message=DUPLICATE_ITEM_ERROR
            )
        ]


class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, source="item_set")

    class Meta:
        model = List
        fields = ("id", "items",)


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


router = routers.SimpleRouter()
router.register(r"lists", ListViewSet)
router.register(r"items", ItemViewSet)
