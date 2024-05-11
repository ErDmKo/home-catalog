from django.shortcuts import render

from .models import CatalogItem


def index(request):
    return render(
        request,
        "catalog/index.html",
        {"latest_catalog_list": CatalogItem.objects.order_by("-pub_date")[:100]},
    )
