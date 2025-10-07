from rest_framework import serializers, viewsets, filters, permissions, status, mixins
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
    slugify_function,
    CatalogGroup,
    CatalogGroupInvitation,
    ItemDefinition,
    CatalogEntry,
)

from .serializers import (
    CatalogGroupSerializer,
    CatalogGroupInvitationSerializer,
    ItemDefinitionSerializer,
)


class CatalogResourceSerializer(ItemDefinitionSerializer):
    """
    Serializes an ItemDefinition and enriches it with the current user's
    catalog-specific information, like the 'to_buy' status.
    This creates a unified "CatalogResource" for the frontend.
    """

    to_buy = serializers.SerializerMethodField()

    class Meta(ItemDefinitionSerializer.Meta):
        fields = ItemDefinitionSerializer.Meta.fields + ["to_buy"]

    def get_to_buy(self, obj):
        """
        Returns the 'to_buy' status for the current user.
        Defaults to False if no CatalogEntry exists.
        """
        user = self.context["request"].user
        if user.is_anonymous:
            return False

        try:
            entry = CatalogEntry.objects.get(
                item_definition=obj, catalog_group__owners=user
            )
            return entry.to_buy
        except CatalogEntry.DoesNotExist:
            return False


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


class CatalogResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that presents a unified view of catalog items for the current user.
    It allows searching all available items and updating the user-specific
    'to_buy' status for each item.
    """

    queryset = ItemDefinition.objects.all().order_by("name")
    serializer_class = CatalogResourceSerializer
    filter_backends = [MyBackend]
    search_fields = ["slug", "group__slug"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures the request context is passed to the serializer.
        """
        return {"request": self.request}

    def partial_update(self, request, *args, **kwargs):
        """
        Handles PATCH requests to update the 'to_buy' status for an item.
        This will get or create a CatalogEntry as needed.
        """
        instance = self.get_object()
        to_buy = request.data.get("to_buy")

        if to_buy is None:
            return Response(
                {"error": "The 'to_buy' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        catalog_group = CatalogGroup.objects.filter(owners=user).first()

        if not catalog_group:
            return Response(
                {"error": "You do not own a catalog group."},
                status=status.HTTP_403_FORBIDDEN,
            )

        entry, created = CatalogEntry.objects.get_or_create(
            item_definition=instance,
            catalog_group=catalog_group,
            defaults={"to_buy": to_buy},
        )

        if not created:
            entry.to_buy = to_buy
            entry.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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
