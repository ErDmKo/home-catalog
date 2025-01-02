from rest_framework import viewsets, filters

from .models import CatalogItem, ItemGroup
from .serializers import CatalogItemSerializer


class CatalogItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows catalog items to be managed (view, careate, delete)
    """

    queryset = CatalogItem.objects.all().order_by("name")
    serializer_class = CatalogItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "group__title"]
