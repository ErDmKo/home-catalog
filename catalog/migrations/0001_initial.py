# Generated by Django 5.0.4 on 2024-04-27 16:28

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CatalogItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("count", models.IntegerField(default=0)),
                ("pub_date", models.DateTimeField(verbose_name="date published")),
            ],
        ),
    ]