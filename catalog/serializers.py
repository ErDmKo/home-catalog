from rest_framework import serializers

from .models import CatalogItem, ItemGroup, CatalogGroup, CatalogGroupInvitation


class ItemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemGroup
        fields = ["title"]


class CatalogGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogGroup
        fields = ["name", "owners"]


class CatalogItemSerializer(serializers.ModelSerializer):
    group = ItemGroupSerializer(many=True, read_only=True)

    class Meta:
        model = CatalogItem
        fields = ["name", "group", "to_buy", "pk", "catalog_group"]


class CatalogGroupInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogGroupInvitation
        fields = ["id", "catalog_group", "invited_by", "created_at"]
        read_only_fields = ["id", "catalog_group", "invited_by", "created_at"]
