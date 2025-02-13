from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import CatalogGroup, ItemGroup, CatalogItem


class CatalogGroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.catalog_group = CatalogGroup.objects.create(name='Test Catalog')
        self.catalog_group.owners.add(self.user)

    def test_catalog_group_creation(self):
        """Test that a catalog group can be created with proper attributes"""
        self.assertEqual(self.catalog_group.name, 'Test Catalog')
        self.assertIn(self.user, self.catalog_group.owners.all())

    def test_catalog_group_str(self):
        """Test the string representation of CatalogGroup"""
        self.assertEqual(str(self.catalog_group), 'Test Catalog')


class ItemGroupTests(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(title='Test Group')

    def test_item_group_creation(self):
        """Test that an item group can be created with proper attributes"""
        self.assertEqual(self.item_group.title, 'Test Group')
        self.assertEqual(self.item_group.slug, 'test-group')

    def test_item_group_str(self):
        """Test the string representation of ItemGroup"""
        self.assertEqual(str(self.item_group), 'Test Group')


class CatalogItemTests(TestCase):
    def setUp(self):
        self.catalog_group = CatalogGroup.objects.create(name='Test Catalog')
        self.item_group = ItemGroup.objects.create(title='Test Group')
        self.catalog_item = CatalogItem.objects.create(
            name='Test Item',
            catalog_group=self.catalog_group,
            count=5.5,
            to_buy=True,
            pub_date=timezone.now()
        )
        self.catalog_item.group.add(self.item_group)

    def test_catalog_item_creation(self):
        """Test that a catalog item can be created with proper attributes"""
        self.assertEqual(self.catalog_item.name, 'Test Item')
        self.assertEqual(self.catalog_item.slug, 'test-item')
        self.assertEqual(self.catalog_item.catalog_group, self.catalog_group)
        self.assertEqual(self.catalog_item.count, 5.5)
        self.assertTrue(self.catalog_item.to_buy)
        self.assertIn(self.item_group, self.catalog_item.group.all())

    def test_catalog_item_str(self):
        """Test the string representation of CatalogItem"""
        expected_str = '[Test Group] Test Item'
        self.assertEqual(str(self.catalog_item), expected_str)
