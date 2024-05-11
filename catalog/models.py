from django.db import models


class CatalogItem(models.Model):
    name = models.CharField("Наименование вещи", unique=True, max_length=200)
    count = models.DecimalField(
        "Количество", default=0, max_digits=100, decimal_places=5
    )
    pub_date = models.DateTimeField("Дата публикации")
    ordering = ["name"]

    class Meta:
        indexes = [models.Index(fields=["name"], name="name_idx")]

    def __str__(self):
        return f"{self.name} ({self.count})"
