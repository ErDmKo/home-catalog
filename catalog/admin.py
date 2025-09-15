from django.contrib import admin

from .models import (
    CatalogItem,
    ItemGroup,
    CatalogGroup,
    ItemDefinition,
    CatalogEntry,
)


@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]


@admin.register(CatalogGroup)
class CatalogGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemDefinition)
class ItemDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name__icontains", "group__title"]
    ordering = ["name", "pk"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CatalogEntry)
class CatalogEntryAdmin(admin.ModelAdmin):
    list_display = ["item_definition", "catalog_group", "to_buy"]
    list_editable = ["to_buy"]
    list_filter = ["to_buy", "catalog_group"]
    search_fields = ["item_definition__name__icontains"]
    ordering = ["item_definition__name", "pk"]


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "to_buy", "catalog_group"]
    list_filter = ["to_buy", "catalog_group"]
    search_fields = ["name__icontains", "group__title"]
    ordering = ["name", "pk"]
