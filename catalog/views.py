from django.shortcuts import render, redirect
from django.urls import reverse
from .models import CatalogItem


def update(request, catalog_item_id):
    path = reverse("index")
    only_to_by = request.GET.get("only_to_by")
    url_query = ""
    if only_to_by:
        url_query = f"only_to_by={only_to_by}"

    if not request.user.is_authenticated:
        return redirect(f"{path}?{url_query}")
    item = CatalogItem.objects.get(id=catalog_item_id)
    item.to_buy = not item.to_buy
    item.save()
    return redirect(f"{path}?{url_query}")


def index(request):
    query = CatalogItem.objects.all()
    only_to_by = request.GET.get("only_to_by", "")
    if only_to_by:
        query = CatalogItem.objects.filter(to_buy=True)
    return render(
        request,
        "catalog/index.html",
        {"only_to_by": only_to_by, "latest_catalog_list": query[:100]},
    )
