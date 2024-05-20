from django.db import models
from datetime import datetime

class ItemGroup(models.Model):
    title = models.CharField("Название группы", max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Группы вещей"

class CatalogItem(models.Model):
    name = models.CharField("Наименование вещи", unique=True, max_length=200)
    count = models.DecimalField(
        "Количество", default=0, max_digits=100, decimal_places=5
    )
    pub_date = models.DateTimeField("Дата публикации", default=datetime.now)
    to_buy = models.BooleanField("Нужно купить", default=False)
    group = models.ManyToManyField(ItemGroup, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"], name="name_idx")]
        verbose_name_plural = "Каталог вещей"

    def __str__(self):
        grops = "".join([f"[{group.title}]" for group in self.group.all()])
        return f"{grops} {self.name} ({self.count:.2f})"
