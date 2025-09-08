from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.conf import settings

from catalog.models import CatalogGroup, CatalogGroupInvitation


class InvitationAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="testpassword")
        self.user2 = User.objects.create_user(username="user2", password="testpassword")
        self.admin_user = User.objects.create_superuser(
            username="adminuser", password="adminpassword"
        )
        self.group1 = CatalogGroup.objects.create(name="User1's Group")
        self.group1.owners.add(self.user1)

    def test_owner_can_create_invitation(self):
        """Ensure an owner of a catalog can create an invitation."""
        self.client.login(username="user1", password="testpassword")
        url = reverse(
            "catalog:cataloggroup-create-invitation", kwargs={"pk": self.group1.pk}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CatalogGroupInvitation.objects.count(), 1)
        self.assertEqual(CatalogGroupInvitation.objects.first().invited_by, self.user1)

    def test_non_owner_cannot_create_invitation(self):
        """Ensure a user who is not an owner cannot create an invitation."""
        self.client.login(username="user2", password="testpassword")
        url = reverse(
            "catalog:cataloggroup-create-invitation", kwargs={"pk": self.group1.pk}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_new_user_can_accept_valid_invitation(self):
        """Ensure a user with no catalog can accept a valid invitation."""
        self.client.login(username="user2", password="testpassword")
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1
        )
        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group1.refresh_from_db()
        self.assertIn(self.user2, self.group1.owners.all())
        invitation.refresh_from_db()
        self.assertEqual(invitation.accepted_by, self.user2)

    def test_cannot_accept_expired_invitation(self):
        """Ensure an expired invitation cannot be accepted."""
        self.client.login(username="user2", password="testpassword")
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1
        )
        # Manually expire the invitation
        invitation.created_at = timezone.now() - timedelta(
            days=settings.INVITATION_EXPIRATION_DAYS + 1
        )
        invitation.save()

        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_cannot_accept_already_used_invitation(self):
        """Ensure a previously accepted invitation cannot be reused."""
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1, accepted_by=self.user1
        )
        self.client.login(username="user2", password="testpassword")
        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_invite_returns_conflict_for_existing_owner(self):
        """
        Ensure a 409 Conflict is returned if an invited user already owns a catalog.
        """
        group2 = CatalogGroup.objects.create(name="User2's Group")
        group2.owners.add(self.user2)

        self.client.login(username="user2", password="testpassword")
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1
        )
        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("CATALOG_OWNERSHIP_CONFLICT", response.data.get("code", ""))

    def test_user_can_accept_and_leave_existing_catalog(self):
        """
        Ensure a user can leave their old catalog to accept an invitation to a new one.
        """
        group2 = CatalogGroup.objects.create(name="User2's Group")
        group2.owners.add(self.user2)

        self.client.login(username="user2", password="testpassword")
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1
        )
        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url, {"accept_and_leave": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify user is in the new group
        self.group1.refresh_from_db()
        self.assertIn(self.user2, self.group1.owners.all())
        # Verify user is no longer in the old group
        group2.refresh_from_db()
        self.assertNotIn(self.user2, group2.owners.all())

    def test_admin_can_join_second_catalog_without_leaving(self):
        """Ensure an admin can join a new catalog without leaving their old one."""
        admin_group = CatalogGroup.objects.create(name="Admin's Group")
        admin_group.owners.add(self.admin_user)

        self.client.login(username="adminuser", password="adminpassword")
        invitation = CatalogGroupInvitation.objects.create(
            catalog_group=self.group1, invited_by=self.user1
        )
        url = reverse("catalog:invitation-accept", kwargs={"pk": invitation.pk})
        response = self.client.post(url)  # No `accept_and_leave` flag

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify admin is in the new group
        self.group1.refresh_from_db()
        self.assertIn(self.admin_user, self.group1.owners.all())
        # Verify admin is still in their original group
        admin_group.refresh_from_db()
        self.assertIn(self.admin_user, admin_group.owners.all())
