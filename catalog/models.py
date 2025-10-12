from slugify import slugify
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import uuid


class CatalogGroup(models.Model):
    name = models.CharField("Catalog Name", unique=True, max_length=200)
    owners = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Catalogs"


class ItemGroup(models.Model):
    title = models.CharField("Group Name", max_length=200, unique=True)
    slug = models.SlugField("slug", default="-", unique=True)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify_function(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Item Groups"


def slugify_function(content):
    return slugify(content)


# TODO: This model should be removed after the data migration is complete.
class CatalogItem(models.Model):
    name = models.CharField("Item Name", unique=True, max_length=200)
    catalog_group = models.ForeignKey(
        CatalogGroup, on_delete=models.CASCADE, blank=True, null=True
    )
    count = models.DecimalField("Quantity", default=0, max_digits=100, decimal_places=5)
    pub_date = models.DateTimeField("Publication Date", default=timezone.now)
    to_buy = models.BooleanField("To Buy", default=False)
    group = models.ManyToManyField(ItemGroup, blank=True)
    slug = models.SlugField("slug", default="-")

    def save(self, *args, **kwargs):
        self.slug = slugify_function(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = [models.F("group__title"), "name"]
        indexes = [models.Index(fields=["name"], name="name_idx")]
        verbose_name_plural = "Catalog Items (Old)"

    def __str__(self):
        grops = "".join([f"[{group.title}]" for group in self.group.all()])
        return f"{grops} {self.name}"


class ItemDefinition(models.Model):
    name = models.CharField("Item Name", unique=True, max_length=200)
    group = models.ManyToManyField(ItemGroup, blank=True)
    slug = models.SlugField("slug", default="-")

    def save(self, *args, **kwargs):
        self.slug = slugify_function(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = [models.F("group__title"), "name"]
        indexes = [models.Index(fields=["name"], name="item_definition_name_idx")]
        verbose_name_plural = "Item Definitions"

    def __str__(self):
        grops = "".join([f"[{group.title}]" for group in self.group.all()])
        return f"{grops} {self.name}"


class CatalogEntry(models.Model):
    item_definition = models.ForeignKey(ItemDefinition, on_delete=models.CASCADE)
    catalog_group = models.ForeignKey(CatalogGroup, on_delete=models.CASCADE, null=True, blank=True)
    count = models.DecimalField("Quantity", default=0, max_digits=100, decimal_places=5)
    pub_date = models.DateTimeField("Publication Date", default=timezone.now)
    to_buy = models.BooleanField("To Buy", default=False)

    class Meta:
        ordering = ["item_definition__name"]
        verbose_name_plural = "Catalog Entries"
        unique_together = ("item_definition", "catalog_group")

    def __str__(self):
        if self.catalog_group is None:
            return f"{self.item_definition.name} in No Catalog"
        return f"{self.item_definition.name} in {self.catalog_group.name}"


class CatalogGroupInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalog_group = models.ForeignKey(
        CatalogGroup, on_delete=models.CASCADE, related_name="invitations"
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invitations"
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invitations",
    )
    created_at = models.DateTimeField(auto_now_add=True)  # For TTL

    def __str__(self):
        return f"Invitation to {self.catalog_group.name} by {self.invited_by.username}"
