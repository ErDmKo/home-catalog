from django.contrib.auth.models import User
from django.utils import timezone

from ..models import CatalogGroup, ItemGroup, ItemDefinition, CatalogEntry


def create_user(username="testuser", password="12345"):
    return User.objects.create_user(username=username, password=password)


def create_catalog_group(name="Test Catalog", owner=None):
    group = CatalogGroup.objects.create(name=name)
    if owner:
        group.owners.add(owner)
    return group


def create_item_group(title="Test Group"):
    return ItemGroup.objects.create(title=title)


def create_item_definition(name="Test Item Definition", group=None):
    item_def = ItemDefinition.objects.create(name=name)
    if group:
        item_def.group.add(group)
    return item_def


def create_catalog_entry(item_definition, catalog_group, to_buy=False, count=0):
    return CatalogEntry.objects.create(
        item_definition=item_definition,
        catalog_group=catalog_group,
        to_buy=to_buy,
        count=count,
        pub_date=timezone.now(),
    )
