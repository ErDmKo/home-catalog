from django.contrib import admin

from .models import CatalogItem, ItemGroup

@admin.register(ItemGroup)
class ItemGroupAdmin(admin.ModelAdmin):
    pass

@admin.display
def catalog_item_name(obj):
    return str(obj)

@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = [catalog_item_name, "to_buy"]
    list_editable = ["to_buy"]
    list_filter = ["to_buy"]
    search_fields = ["name__icontains", "group__title"]
    ordering = ["name", "pk"]

