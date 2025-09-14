from rest_framework import viewsets, filters, permissions, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from django.utils.text import smart_split, unescape_string_literal
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    CatalogItem,
    slugify_function,
    CatalogGroup,
    CatalogGroupInvitation,
)

from .serializers import (
    CatalogItemSerializer,
    CatalogGroupSerializer,
    CatalogGroupInvitationSerializer,
)


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
        serializer.save(owners=[user])

    @action(detail=True, methods=["post"], url_path="create-invitation")
    def create_invitation(self, request, pk=None):
        catalog_group = self.get_object()
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=catalog_group, invited_by=request.user
        )
        serializer = CatalogGroupInvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class InvitationViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = CatalogGroupInvitation.objects.all()
    serializer_class = CatalogGroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def accept(self, request, pk=None):
        invitation = self.get_object()
        user = request.user
        accept_and_leave = request.data.get("accept_and_leave", False)

        # 1. Check if invitation is still valid
        if invitation.accepted_by:
            return Response(
                {"error": "This invitation has already been accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Check for TTL expiration
        expiration_date = invitation.created_at + timedelta(
            days=settings.INVITATION_EXPIRATION_DAYS
        )
        if timezone.now() > expiration_date:
            return Response(
                {"error": "This invitation has expired."},
                status=status.HTTP_410_GONE,
            )

        # 3. Handle user with an existing catalog
        existing_group = CatalogGroup.objects.filter(owners=user).first()
        if existing_group and not user.is_superuser:
            if not accept_and_leave:
                return Response(
                    {
                        "code": "CATALOG_OWNERSHIP_CONFLICT",
                        "error": "You already own a catalog. To join a new one, you must leave your current one.",
                        "conflicting_catalog_name": existing_group.name,
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            # User confirmed leaving their old group
            existing_group.owners.remove(user)

        # 4. Add user to the new group and update invitation
        invitation.catalog_group.owners.add(user)
        invitation.accepted_by = user
        invitation.save()

        return Response(
            {"status": f"Successfully joined {invitation.catalog_group.name}."},
            status=status.HTTP_200_OK,
        )
