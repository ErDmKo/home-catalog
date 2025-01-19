from functools import reduce
import operator

from rest_framework import viewsets, filters
from rest_framework.fields import CharField
from django.db import models
from django.utils.text import smart_split, unescape_string_literal

from .models import CatalogItem, ItemGroup, slugify_function
from .serializers import CatalogItemSerializer


def search_smart_split(search_terms):
    """Returns sanitized search terms as a list."""
    split_terms = []
    for term in smart_split(search_terms):
        # trim commas to avoid bad matching for quoted phrases
        term = term.strip(",")

        if term.startswith(('"', "'")) and term[0] == term[-1]:
            # quoted phrases are kept together without any other split
            split_terms.append(unescape_string_literal(term))
        else:
            # non-quoted tokens are split by comma, keeping only non-empty ones
            for sub_term in term.split(","):
                if sub_term:
                    split_terms.append(sub_term.strip())
    return split_terms


class MyBackend(filters.SearchFilter):
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be whitespace delimited.
        """
        value = request.query_params.get(self.search_param, "")
        print(value)
        slugifyed_value = slugify_function(value)
        field = CharField(trim_whitespace=False, allow_blank=True)
        cleaned_value = field.run_validation(slugifyed_value)
        return search_smart_split(cleaned_value)


class CatalogItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows catalog items to be managed (view, careate, delete)
    """

    queryset = CatalogItem.objects.all().order_by("name")
    serializer_class = CatalogItemSerializer
    filter_backends = [MyBackend]
    search_fields = ["slug", "group__slug"]
