from django.db import models

class CatalogItem(models.Model):
    name = models.CharField(max_length=200)
    count = models.DecimalField(
        default=0,
        max_digits=100,
        decimal_places=5
    )
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return f'{self.name} ({self.count})'
