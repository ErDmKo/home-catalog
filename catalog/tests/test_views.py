from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import CatalogGroup, ItemGroup, ItemDefinition, CatalogEntry


class CatalogListViewTests(TestCase):
    def setUp(self):
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

        self.client.login(username="testuser", password="12345")

    def test_view_requires_login(self):
        """Test that view redirects to login page for anonymous users"""
        self.client.logout()
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/catalog/login/", response.url)

    def test_context_data(self):
        """Test that all required context data is present"""
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)

        self.assertIn("query_dict", response.context)
        self.assertIn("query", response.context)
        self.assertIn("groups", response.context)
        self.assertIn("selected_group", response.context)
        self.assertIn("latest_catalog_list", response.context)

    def test_selected_group_with_invalid_id(self):
        """Test handling of invalid group ID"""
        response = self.client.get(reverse("catalog:index") + "?group=999")
        self.assertEqual(response.status_code, 404)

    def test_filter_by_to_buy(self):
        """Test filtering items by to_buy status"""
        item_def = ItemDefinition.objects.create(name="Another Test Item")
        to_buy_entry = CatalogEntry.objects.create(
            item_definition=item_def,
            catalog_group=self.catalog_group,
            to_buy=True,
        )
        response = self.client.get(reverse("catalog:index") + "?only_to_by=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(to_buy_entry, response.context["latest_catalog_list"])
        self.assertNotIn(self.entry, response.context["latest_catalog_list"])

    def test_filter_by_group(self):
        """Test filtering items by group"""
        other_group = ItemGroup.objects.create(title="Other Group")
        other_item_def = ItemDefinition.objects.create(name="Other Item Definition")
        other_item_def.group.add(other_group)
        other_entry = CatalogEntry.objects.create(
            item_definition=other_item_def,
            catalog_group=self.catalog_group,
        )

        response = self.client.get(f'{reverse("catalog:index")}?group={self.group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.entry, response.context["latest_catalog_list"])
        self.assertNotIn(other_entry, response.context["latest_catalog_list"])

    def test_flat_view(self):
        """Test flat view mode"""
        response = self.client.get(reverse("catalog:index") + "?flat_view=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["groups"]), [])


class UpdateEntryStatusViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        self.catalog_group.owners.add(self.user)
        self.item_definition = ItemDefinition.objects.create(
            name="Test Item Definition"
        )
        self.entry = CatalogEntry.objects.create(
            item_definition=self.item_definition,
            catalog_group=self.catalog_group,
            to_buy=False,
        )
        self.client.login(username="testuser", password="12345")

    def test_post_toggles_to_buy(self):
        """Test that POST request toggles to_buy status"""
        response = self.client.post(reverse("catalog:update", args=[self.entry.id]))
        self.entry.refresh_from_db()

        self.assertTrue(self.entry.to_buy)
        self.assertRedirects(response, reverse("catalog:index"))

    def test_get_returns_bad_request(self):
        """Test that GET request returns 400 Bad Request"""
        response = self.client.get(reverse("catalog:update", args=[self.entry.id]))
        self.assertEqual(response.status_code, 400)

    def test_post_preserves_query_params(self):
        """Test that query parameters are preserved after update"""
        response = self.client.post(
            reverse("catalog:update", args=[self.entry.id]) + "?only_to_by=1"
        )
        self.assertIn("only_to_by=1", response.url)

    def test_update_nonexistent_item(self):
        """Test updating a non-existent item returns 404"""
        response = self.client.post(reverse("catalog:update", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_update_unauthorized_item(self):
        """Test updating an item owned by another user"""
        other_user = User.objects.create_user(username="other", password="12345")
        other_catalog = CatalogGroup.objects.create(name="Other Catalog")
        other_catalog.owners.add(other_user)
        other_item_def = ItemDefinition.objects.create(name="Other Item Definition")
        other_entry = CatalogEntry.objects.create(
            item_definition=other_item_def, catalog_group=other_catalog
        )

        response = self.client.post(reverse("catalog:update", args=[other_entry.id]))
        self.assertEqual(response.status_code, 404)

    def test_update_requires_login(self):
        """Test that update view requires login"""
        self.client.logout()
        response = self.client.post(reverse("catalog:update", args=[self.entry.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/catalog/login/", response.url)


class CatalogResourceCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        self.catalog_group.owners.add(self.user)
        self.client.login(username="testuser", password="12345")

    def test_create_new_item_and_entry(self):
        """Test creating a new ItemDefinition and CatalogEntry"""
        response = self.client.post(
            reverse("catalog:create"), {"name": "New Item", "group": []}
        )
        self.assertEqual(ItemDefinition.objects.count(), 1)
        self.assertEqual(CatalogEntry.objects.count(), 1)

        item_def = ItemDefinition.objects.first()
        self.assertEqual(item_def.name, "New Item")

        entry = CatalogEntry.objects.first()
        self.assertEqual(entry.item_definition, item_def)
        self.assertEqual(entry.catalog_group, self.catalog_group)
        self.assertTrue(entry.to_buy)
        self.assertRedirects(response, reverse("catalog:index"))

    def test_form_prefilled_with_name_query_param(self):
        """Test that form is prefilled with name from query parameter"""
        response = self.client.get(reverse("catalog:create") + "?name=Test+Item")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial.get("name"), "Test Item")

    def test_form_prefilled_with_group_query_param(self):
        """Test that form is prefilled with group from query parameter"""
        group = ItemGroup.objects.create(title="Test Group")
        response = self.client.get(reverse("catalog:create") + f"?group={group.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial.get("group"), [str(group.id)])

    def test_success_url_preserves_query_params(self):
        """Test that query parameters are preserved in success URL"""
        response = self.client.post(
            reverse("catalog:create") + "?group=1", {"name": "New Item", "group": []}
        )
        self.assertIn("group=1", response.url)

    def test_requires_login(self):
        """Test that view requires login"""
        self.client.logout()
        response = self.client.get(reverse("catalog:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/catalog/login/", response.url)


class CatalogLoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_redirect_authenticated_user_without_catalog(self):
        """Test that authenticated users without a catalog are redirected to the create catalog page"""
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("catalog:login"))
        self.assertRedirects(response, reverse("catalog:create-catalog-group"))

    def test_redirect_authenticated_user_with_catalog(self):
        """Test that authenticated users with a catalog are redirected to the index page"""
        catalog_group = CatalogGroup.objects.create(name="Test Catalog")
        catalog_group.owners.add(self.user)
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("catalog:login"))
        self.assertRedirects(response, reverse("catalog:index"))

    def test_shows_login_page_for_anonymous(self):
        """Test that anonymous users see the login page"""
        response = self.client.get(reverse("catalog:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/auth.html")
