from urllib.parse import urlencode, quote

from django.views.generic.edit import CreateView

from django.shortcuts import render, redirect
from .models import CatalogItem, ItemGroup, CatalogGroup
from django.db.models import Q
from django.urls import reverse_lazy

query_parmas = ["only_to_by", "group", "flat_view", "error"]


class ItemCreateView(CreateView):
    model = CatalogItem
    fields = ["name", "group"]
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        user = self.request.user
        instance = form.instance
        catalog_query = CatalogGroup.objects.filter(owners=user.id)
        instance.catalog_group = catalog_query[0]
        self.object = form.save()
        return super().form_valid(form)

    def get_initial(self):
        name = self.request.GET.get("name")
        return {"name": name}


def encode(str_query):
    return urlencode(str_query, quote_via=quote)


def get_query_state(request):
    return_dict = {}
    for param in query_parmas:
        value = request.GET.get(param)
        if value:
            return_dict[param] = value
    return return_dict


def update(request, catalog_item_id):
    path = reverse_lazy("index")
    query = encode(get_query_state(request))
    if not request.user.is_authenticated:
        error_query = encode({"error": "not authenticated"})
        return redirect(f"{path}?{error_query}")
    item = CatalogItem.objects.get(id=catalog_item_id)
    item.to_buy = not item.to_buy
    item.save()
    return redirect(f"{path}?{query}")


def index(request):
    list_query = Q(to_buy=False)
    if not request.user.is_authenticated:
        return render(request, "catalog/auth.html", {})
    groups = ItemGroup.objects.filter().distinct()
    query_dict = get_query_state(request)
    selected_group = None
    if query_dict.get("only_to_by"):
        groups = ItemGroup.objects.filter(catalogitem__to_buy=True).distinct()
        list_query = Q(to_buy=True)
    if query_dict.get("group"):
        groups = ItemGroup.objects.none()
        selected_group = ItemGroup.objects.get(id=query_dict["group"])
        list_query = list_query & Q(group=query_dict["group"])
    elif query_dict.get("flat_view"):
        groups = ItemGroup.objects.none()
    else:
        list_query = list_query & Q(group=None)
    list_query = list_query & Q(catalog_group__owners=request.user)
    groups = (
        groups
        & ItemGroup.objects.filter(
            catalogitem__catalog_group__owners=request.user
        ).distinct()
    )
    str_query = encode(query_dict)
    return render(
        request,
        "catalog/index.html",
        {
            "query_dict": query_dict,
            "query": str_query,
            "fileds_to_safe": query_parmas,
            "groups": groups,
            "selected_group": selected_group,
            "latest_catalog_list": CatalogItem.objects.filter(list_query),
        },
    )
