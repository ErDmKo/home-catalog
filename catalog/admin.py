from django.contrib import admin

from .models import CatalogItem


@admin.register(CatalogItem)
class CatalodItemAdmin(admin.ModelAdmin):
    list_display = ["name", "count"]
    list_editable = ["count"]
    list_filter = ["count"]
    search_fields = ["name__icontains"]
    ordering = ["name", "pk"]
