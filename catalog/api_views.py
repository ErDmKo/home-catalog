from rest_framework import viewsets, filters, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from django.utils.text import smart_split, unescape_string_literal

from .models import CatalogItem, slugify_function, CatalogGroup
from .serializers import CatalogItemSerializer, CatalogGroupSerializer


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


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user in obj.owners.all() or request.user.is_superuser


class MyBackend(filters.SearchFilter):
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be whitespace delimited.
        """
        value = request.query_params.get(self.search_param, "")
        slugifyed_value = slugify_function(value)
        field = CharField(trim_whitespace=False, allow_blank=True)
        cleaned_value = field.run_validation(slugifyed_value)
        return search_smart_split(cleaned_value)


class CatalogGroupViewSet(viewsets.ModelViewSet):
    queryset = CatalogGroup.objects.all()
    serializer_class = CatalogGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if self.action == "list" and not user.is_superuser:
            return super().get_queryset().filter(owners=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser and CatalogGroup.objects.filter(owners=user).exists():
            raise ValidationError("You can only have one catalog group.")
        instance = serializer.save()
        instance.owners.add(user)


class CatalogItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows catalog items to be managed (view, careate, delete)
    """

    queryset = CatalogItem.objects.all().order_by("name")
    serializer_class = CatalogItemSerializer
    filter_backends = [MyBackend]
    search_fields = ["slug", "group__slug"]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(catalog_group__owners=user.id)
