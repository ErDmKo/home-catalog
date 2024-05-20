from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.urls import reverse
from .models import CatalogItem, ItemGroup
from django.db.models import Q

query_parmas = ["only_to_by", "group"]


def get_query_state(request):
    return_dict = {}
    for param in query_parmas:
        value = request.GET.get(param)
        if value:
            return_dict[param] = value
    return return_dict


def update(request, catalog_item_id):
    path = reverse("index")
    query = urlencode(get_query_state(request))
    if not request.user.is_authenticated:
        return redirect(f"{path}?{query}")
    item = CatalogItem.objects.get(id=catalog_item_id)
    item.to_buy = not item.to_buy
    item.save()
    return redirect(f"{path}?{query}")


def index(request):
    list_query = Q(to_buy=False)
    groups = ItemGroup.objects.all().distinct()
    query_dict = get_query_state(request)
    selected_group = None
    if query_dict.get("only_to_by"):
        groups = ItemGroup.objects.filter(catalogitem__to_buy=True).distinct()
        list_query = Q(to_buy=True)
    if query_dict.get("group"):
        groups = []
        selected_group = ItemGroup.objects.get(id=query_dict["group"])
        list_query = list_query & Q(group=query_dict["group"])
    else:
        list_query = list_query & Q(group=None)
    return render(
        request,
        "catalog/index.html",
        {
            "query_dict": query_dict,
            "query": urlencode(query_dict),
            "groups": groups,
            "selected_group": selected_group,
            "latest_catalog_list": CatalogItem.objects.filter(list_query),
        },
    )
