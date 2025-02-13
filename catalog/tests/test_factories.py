from django.contrib.auth.models import User
from django.utils import timezone

from ..models import CatalogGroup, ItemGroup, CatalogItem


def create_user(username="testuser", password="12345"):
    return User.objects.create_user(username=username, password=password)


def create_catalog_group(name="Test Catalog", owner=None):
    group = CatalogGroup.objects.create(name=name)
    if owner:
        group.owners.add(owner)
    return group


def create_item_group(title="Test Group"):
    return ItemGroup.objects.create(title=title)


def create_catalog_item(name="Test Item", catalog_group=None, group=None, to_buy=False):
    item = CatalogItem.objects.create(
        name=name, catalog_group=catalog_group, to_buy=to_buy, pub_date=timezone.now()
    )
    if group:
        item.group.add(group)
    return item
