from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class CatalogGroup(models.Model):
    name = models.CharField("Наименование каталога", unique=True, max_length=200)
    owners = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Каталоги"


class ItemGroup(models.Model):
    title = models.CharField("Название группы", max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Группы вещей"


class CatalogItem(models.Model):
    name = models.CharField("Наименование вещи", unique=True, max_length=200)
    catalog_group = models.ForeignKey(
        CatalogGroup, on_delete=models.CASCADE, blank=True, null=True
    )
    count = models.DecimalField(
        "Количество", default=0, max_digits=100, decimal_places=5
    )
    pub_date = models.DateTimeField("Дата публикации", default=datetime.now)
    to_buy = models.BooleanField("Нужно купить", default=False)
    group = models.ManyToManyField(ItemGroup, blank=True)

    class Meta:
        ordering = [models.F("group__title"), "name"]
        indexes = [models.Index(fields=["name"], name="name_idx")]
        verbose_name_plural = "Каталог вещей"

    def __str__(self):
        grops = "".join([f"[{group.title}]" for group in self.group.all()])
        return f"{grops} {self.name} ({self.count:.2f})"
