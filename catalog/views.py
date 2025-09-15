from urllib.parse import urlencode, quote
from django.views.generic import ListView, View, TemplateView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest

from .models import ItemDefinition, CatalogEntry, ItemGroup, CatalogGroup


class QueryParamsMixin:
    """Mixin to handle query parameter validation and filtering"""

    VALID_PARAMS = {"only_to_by", "group", "flat_view", "error"}

    def get_query_state(self):
        """Get validated query parameters from request"""
        if not hasattr(self, "_query_state"):
            self._query_state = {
                k: v
                for k, v in self.request.GET.items()
                if k in self.VALID_PARAMS and v
            }
        return self._query_state

    def encode_query(self, params=None):
        """Encode query parameters to URL string"""
        query_dict = params if params is not None else self.get_query_state()
        return urlencode(query_dict, quote_via=quote)

    def build_entry_query(self):
        """Build query for CatalogEntry filtering"""
        query = Q(catalog_group__owners=self.request.user)
        params = self.get_query_state()

        if params.get("only_to_by"):
            query &= Q(to_buy=True)
        else:
            query &= Q(to_buy=False)

        if params.get("group"):
            query &= Q(item_definition__group=params["group"])
        elif not params.get("flat_view"):
            query &= Q(item_definition__group=None)

        return query

    def get_groups_query(self):
        """Build query for ItemGroup filtering"""
        params = self.get_query_state()
        groups = ItemGroup.objects.filter(
            itemdefinition__catalogentry__catalog_group__owners=self.request.user
        ).distinct()

        if params.get("only_to_by"):
            groups = groups.filter(itemdefinition__catalogentry__to_buy=True)

        if params.get("group") or params.get("flat_view"):
            groups = ItemGroup.objects.none()

        return groups


class CatalogListView(LoginRequiredMixin, QueryParamsMixin, ListView):
    model = CatalogEntry
    template_name = "catalog/index.html"
    context_object_name = "latest_catalog_list"

    def get_queryset(self):
        return self.model.objects.filter(self.build_entry_query())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "query_dict": self.get_query_state(),
                "query": self.encode_query(),
                "groups": self.get_groups_query(),
                "selected_group": self.get_selected_group(),
            }
        )
        return context

    def get_selected_group(self):
        group_id = self.get_query_state().get("group")
        return get_object_or_404(ItemGroup, id=group_id) if group_id else None


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = CatalogEntry
    fields = ["item_definition"]
    success_url = reverse_lazy("catalog:index")

    def form_valid(self, form):
        if not self.request.catalog_group:
            form.add_error(None, "No catalog group found for user")
            return self.form_invalid(form)

        form.instance.catalog_group = self.request.catalog_group
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        item_name = self.request.GET.get("name")
        if item_name:
            item_def, _ = ItemDefinition.objects.get_or_create(name=item_name)
            initial['item_definition'] = item_def
        return initial


class CatalogGroupCreateView(LoginRequiredMixin, CreateView):
    model = CatalogGroup
    fields = ["name"]
    template_name = "catalog/cataloggroup_form.html"
    success_url = reverse_lazy("catalog:index")

    def form_valid(self, form):
        user = self.request.user
        if not user.is_superuser and self.request.catalog_group:
            form.add_error(None, "You can only have one catalog group.")
            return self.form_invalid(form)

        response = super().form_valid(form)
        self.object.owners.add(user)
        return response


class ItemGroupCreateView(LoginRequiredMixin, CreateView):
    model = ItemGroup
    fields = ["title"]
    success_url = reverse_lazy("catalog:index")
    template_name = "catalog/itemgroup_form.html"


class UpdateEntryStatusView(LoginRequiredMixin, QueryParamsMixin, View):
    """Toggle item's to_buy status"""

    def post(self, request, entry_id):
        entry = get_object_or_404(
            CatalogEntry, id=entry_id, catalog_group__owners=request.user
        )
        entry.to_buy = not entry.to_buy
        entry.save()

        return redirect(f"{reverse_lazy('catalog:index')}?{self.encode_query()}")

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest("POST method required")


class CatalogLoginView(TemplateView):
    template_name = "catalog/auth.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("catalog:index")
        return super().dispatch(request, *args, **kwargs)
