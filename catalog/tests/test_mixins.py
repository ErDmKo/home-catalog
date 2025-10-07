from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from ..models import CatalogGroup, ItemGroup, ItemDefinition, CatalogEntry
from ..views import QueryParamsMixin


class QueryParamsMixinTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        self.catalog_group.owners.add(self.user)
        self.group = ItemGroup.objects.create(title="Test Group")

        self.item_definition = ItemDefinition.objects.create(
            name="Test Item Definition"
        )
        self.item_definition.group.add(self.group)

        self.entry = CatalogEntry.objects.create(
            item_definition=self.item_definition,
            catalog_group=self.catalog_group,
        )

    def test_get_query_state_filters_invalid_params(self):
        """Test that get_query_state only returns valid parameters"""
        request = self.factory.get("/?invalid=param&group=1&another=invalid")
        request.user = self.user

        mixin = QueryParamsMixin()
        mixin.request = request

        query_state = mixin.get_query_state()
        self.assertEqual(query_state, {"group": "1"})

    def test_build_entry_query_with_to_buy(self):
        """Test query building with only_to_by parameter"""
        request = self.factory.get("/?only_to_by=1")
        request.user = self.user

        mixin = QueryParamsMixin()
        mixin.request = request

        query = mixin.build_entry_query()
        entries = CatalogEntry.objects.filter(query)

        self.assertQuerySetEqual(entries, [])

    def test_build_entry_query_with_group(self):
        """Test query building with group parameter"""
        request = self.factory.get(f"/?group={self.group.id}")
        request.user = self.user

        mixin = QueryParamsMixin()
        mixin.request = request

        query = mixin.build_entry_query()
        entries = CatalogEntry.objects.filter(query)

        self.assertQuerySetEqual(entries, [self.entry], transform=lambda x: x)

    def test_get_groups_query_with_flat_view(self):
        """Test that flat_view returns no groups"""
        request = self.factory.get("/?flat_view=1")
        request.user = self.user

        mixin = QueryParamsMixin()
        mixin.request = request

        groups = mixin.get_groups_query()
        self.assertQuerySetEqual(groups, [])
