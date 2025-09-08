from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from catalog.models import CatalogGroup


class CatalogGroupAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser", password="adminpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_create_catalog_group(self):
        """
        Ensure we can create a new catalog group.
        """
        url = reverse("catalog:cataloggroup-list")
        data = {"name": "Test Catalog Group"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CatalogGroup.objects.count(), 1)
        self.assertEqual(CatalogGroup.objects.get().name, "Test Catalog Group")
        self.assertIn(self.user, CatalogGroup.objects.get().owners.all())

    def test_user_can_only_create_one_catalog_group(self):
        """
        Ensure that a regular user can only create one catalog group.
        """
        group = CatalogGroup.objects.create(name="First Group")
        group.owners.add(self.user)
        url = reverse("catalog:cataloggroup-list")
        data = {"name": "Second Group"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_create_multiple_catalog_groups(self):
        """
        Ensure that an admin user can create multiple catalog groups.
        """
        self.client.login(username="adminuser", password="adminpassword")
        CatalogGroup.objects.create(name="First Group")
        url = reverse("catalog:cataloggroup-list")
        data = {"name": "Second Group"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CatalogGroup.objects.count(), 2)

    def test_unauthenticated_user_cannot_create_catalog_group(self):
        """
        Ensure that an unauthenticated user cannot create a catalog group.
        """
        self.client.logout()
        url = reverse("catalog:cataloggroup-list")
        data = {"name": "Test Catalog Group"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_catalog_group(self):
        """
        Ensure that an owner can update their catalog group.
        """
        group = CatalogGroup.objects.create(name="Original Name")
        group.owners.add(self.user)
        url = reverse("catalog:cataloggroup-detail", kwargs={"pk": group.pk})
        data = {"name": "Updated Name"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.name, "Updated Name")

    def test_non_owner_cannot_update_catalog_group(self):
        """
        Ensure that a non-owner cannot update a catalog group.
        """
        group = CatalogGroup.objects.create(name="Original Name")
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpassword"
        )
        group.owners.add(another_user)
        url = reverse("catalog:cataloggroup-detail", kwargs={"pk": group.pk})
        data = {"name": "Updated Name"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_catalog_group(self):
        """
        Ensure that an admin can update any catalog group.
        """
        self.client.login(username="adminuser", password="adminpassword")
        group = CatalogGroup.objects.create(name="Original Name")
        url = reverse("catalog:cataloggroup-detail", kwargs={"pk": group.pk})
        data = {"name": "Updated Name"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.name, "Updated Name")
