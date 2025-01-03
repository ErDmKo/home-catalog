from django.contrib import admin

from .models import CatalogItem, ItemGroup, CatalogGroup


@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(CatalogGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    pass


@admin.display
def catalog_item_name(obj):
    return str(obj)


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = [catalog_item_name, "to_buy", "catalog_group"]
    list_editable = ["to_buy", "catalog_group"]
    list_filter = ["to_buy", "catalog_group"]
    search_fields = ["name__icontains", "group__title"]
    ordering = ["name", "pk"]
