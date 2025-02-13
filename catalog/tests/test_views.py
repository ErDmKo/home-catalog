from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import CatalogGroup, ItemGroup, CatalogItem


class CatalogListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.catalog_group = CatalogGroup.objects.create(name='Test Catalog')
        self.catalog_group.owners.add(self.user)
        self.group = ItemGroup.objects.create(title='Test Group')
        
        # Create item first, then add group
        self.item = CatalogItem.objects.create(
            name='Test Item',
            catalog_group=self.catalog_group
        )
        self.item.group.add(self.group)  # Add group through m2m relationship
        
        self.client.login(username='testuser', password='12345')

    def test_view_requires_login(self):
        """Test that view redirects to login page for anonymous users"""
        self.client.logout()
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/catalog/login/', response.url)

    def test_context_data(self):
        """Test that all required context data is present"""
        response = self.client.get(reverse('catalog:index'))
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('query_dict', response.context)
        self.assertIn('query', response.context)
        self.assertIn('groups', response.context)
        self.assertIn('selected_group', response.context)
        self.assertIn('latest_catalog_list', response.context)

    def test_selected_group_with_invalid_id(self):
        """Test handling of invalid group ID"""
        response = self.client.get(reverse('catalog:index') + '?group=999')
        self.assertEqual(response.status_code, 404)

    def test_filter_by_to_buy(self):
        """Test filtering items by to_buy status"""
        to_buy_item = CatalogItem.objects.create(
            name='To Buy Item',
            catalog_group=self.catalog_group,
            to_buy=True
        )
        response = self.client.get(reverse('catalog:index') + '?only_to_by=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(to_buy_item, response.context['latest_catalog_list'])
        self.assertNotIn(self.item, response.context['latest_catalog_list'])

    def test_filter_by_group(self):
        """Test filtering items by group"""
        other_group = ItemGroup.objects.create(title='Other Group')
        other_item = CatalogItem.objects.create(
            name='Other Item',
            catalog_group=self.catalog_group
        )
        other_item.group.add(other_group)

        response = self.client.get(f'{reverse("catalog:index")}?group={self.group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.item, response.context['latest_catalog_list'])
        self.assertNotIn(other_item, response.context['latest_catalog_list'])

    def test_flat_view(self):
        """Test flat view mode"""
        response = self.client.get(reverse('catalog:index') + '?flat_view=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['groups']), [])


class UpdateItemStatusViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.catalog_group = CatalogGroup.objects.create(name='Test Catalog')
        self.catalog_group.owners.add(self.user)
        self.item = CatalogItem.objects.create(
            name='Test Item',
            catalog_group=self.catalog_group,
            to_buy=False
        )
        self.client.login(username='testuser', password='12345')

    def test_post_toggles_to_buy(self):
        """Test that POST request toggles to_buy status"""
        response = self.client.post(
            reverse('catalog:update', args=[self.item.id])
        )
        self.item.refresh_from_db()
        
        self.assertTrue(self.item.to_buy)
        self.assertRedirects(response, reverse('catalog:index'))

    def test_get_returns_bad_request(self):
        """Test that GET request returns 400 Bad Request"""
        response = self.client.get(
            reverse('catalog:update', args=[self.item.id])
        )
        self.assertEqual(response.status_code, 400)

    def test_post_preserves_query_params(self):
        """Test that query parameters are preserved after update"""
        response = self.client.post(
            reverse('catalog:update', args=[self.item.id]) + '?only_to_by=1'
        )
        self.assertIn('only_to_by=1', response.url)

    def test_update_nonexistent_item(self):
        """Test updating a non-existent item returns 404"""
        response = self.client.post(
            reverse('catalog:update', args=[99999])
        )
        self.assertEqual(response.status_code, 404)

    def test_update_unauthorized_item(self):
        """Test updating an item owned by another user"""
        other_user = User.objects.create_user(username='other', password='12345')
        other_catalog = CatalogGroup.objects.create(name='Other Catalog')
        other_catalog.owners.add(other_user)
        other_item = CatalogItem.objects.create(
            name='Other Item',
            catalog_group=other_catalog
        )
        
        response = self.client.post(
            reverse('catalog:update', args=[other_item.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_update_requires_login(self):
        """Test that update view requires login"""
        self.client.logout()
        response = self.client.post(
            reverse('catalog:update', args=[self.item.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/catalog/login/', response.url)


class ItemCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.catalog_group = CatalogGroup.objects.create(name='Test Catalog')
        self.catalog_group.owners.add(self.user)
        self.client.login(username='testuser', password='12345')

    def test_create_item(self):
        """Test creating a new item"""
        response = self.client.post(
            reverse('catalog:create'),
            {'name': 'New Item'}
        )
        self.assertEqual(CatalogItem.objects.count(), 1)
        self.assertRedirects(response, reverse('catalog:index'))

    def test_create_without_catalog_group(self):
        """Test creating item when user has no catalog group"""
        self.catalog_group.delete()
        response = self.client.post(
            reverse('catalog:create'),
            {'name': 'New Item'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CatalogItem.objects.count(), 0)
        
        # Check for error message in response content
        self.assertContains(response, "No catalog group found for user")
        
        # Also check that it's in the form errors
        self.assertIn(
            'No catalog group found for user',
            response.context['form'].non_field_errors()
        )

    def test_create_with_group(self):
        """Test creating an item with a group"""
        group = ItemGroup.objects.create(title='Test Group')
        response = self.client.post(
            reverse('catalog:create'),
            {'name': 'New Item', 'group': [group.id]}
        )
        self.assertEqual(CatalogItem.objects.count(), 1)
        item = CatalogItem.objects.first()
        self.assertIn(group, item.group.all())
        self.assertRedirects(response, reverse('catalog:index'))

    def test_create_requires_login(self):
        """Test that create view requires login"""
        self.client.logout()
        response = self.client.post(
            reverse('catalog:create'),
            {'name': 'New Item'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/catalog/login/', response.url)

    def test_create_with_initial_name(self):
        """Test creating item with name from GET parameter"""
        response = self.client.get(
            reverse('catalog:create') + '?name=Test+Item'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].initial['name'],
            'Test Item'
        )

    def test_create_with_empty_name(self):
        """Test that empty name is not allowed"""
        response = self.client.post(
            reverse('catalog:create'),
            {'name': ''}
        )
        self.assertEqual(response.status_code, 200)  # Form redisplay
        self.assertEqual(CatalogItem.objects.count(), 0)
        
        # Check form errors directly
        self.assertTrue(response.context['form'].errors)
        self.assertIn('name', response.context['form'].errors)
        self.assertEqual(
            response.context['form'].errors['name'][0],
            'This field is required.'
        )


class CatalogLoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_redirects_authenticated_user(self):
        """Test that authenticated users are redirected to index"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('catalog:login'))
        self.assertRedirects(response, reverse('catalog:index'))

    def test_shows_login_page_for_anonymous(self):
        """Test that anonymous users see the login page"""
        response = self.client.get(reverse('catalog:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/auth.html') 