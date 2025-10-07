from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from ..models import CatalogGroup, ItemGroup, ItemDefinition, CatalogEntry


class CatalogGroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        self.catalog_group.owners.add(self.user)

    def test_catalog_group_creation(self):
        """Test that a catalog group can be created with proper attributes"""
        self.assertEqual(self.catalog_group.name, "Test Catalog")
        self.assertIn(self.user, self.catalog_group.owners.all())

    def test_catalog_group_str(self):
        """Test the string representation of CatalogGroup"""
        self.assertEqual(str(self.catalog_group), "Test Catalog")


class ItemGroupTests(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(title="Test Group")

    def test_item_group_creation(self):
        """Test that an item group can be created with proper attributes"""
        self.assertEqual(self.item_group.title, "Test Group")
        self.assertEqual(self.item_group.slug, "test-group")

    def test_item_group_str(self):
        """Test the string representation of ItemGroup"""
        self.assertEqual(str(self.item_group), "Test Group")


class ItemDefinitionTests(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(title="Test Group")
        self.item_definition = ItemDefinition.objects.create(
            name="Test Item Definition"
        )
        self.item_definition.group.add(self.item_group)

    def test_item_definition_creation(self):
        """Test that an item definition can be created with proper attributes"""
        self.assertEqual(self.item_definition.name, "Test Item Definition")
        self.assertEqual(self.item_definition.slug, "test-item-definition")
        self.assertIn(self.item_group, self.item_definition.group.all())

    def test_item_definition_str(self):
        """Test the string representation of ItemDefinition"""
        expected_str = "[Test Group] Test Item Definition"
        self.assertEqual(str(self.item_definition), expected_str)


class CatalogEntryTests(TestCase):
    def setUp(self):
        self.catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        self.item_definition = ItemDefinition.objects.create(
            name="Test Item Definition"
        )
        self.catalog_entry = CatalogEntry.objects.create(
            item_definition=self.item_definition,
            catalog_group=self.catalog_group,
            count=5.5,
            to_buy=True,
            pub_date=timezone.now(),
        )

    def test_catalog_entry_creation(self):
        """Test that a catalog entry can be created with proper attributes"""
        self.assertEqual(self.catalog_entry.item_definition, self.item_definition)
        self.assertEqual(self.catalog_entry.catalog_group, self.catalog_group)
        self.assertEqual(self.catalog_entry.count, 5.5)
        self.assertTrue(self.catalog_entry.to_buy)

    def test_catalog_entry_str(self):
        """Test the string representation of CatalogEntry"""
        expected_str = "Test Item Definition in Test Catalog"
        self.assertEqual(str(self.catalog_entry), expected_str)
