# Generated by Django 5.0.4 on 2024-12-13 19:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_itemgroup_alter_catalogitem_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='catalogitem',
            options={'ordering': [models.F('group__title'), 'name'], 'verbose_name_plural': 'Каталог вещей'},
        ),
        migrations.AlterModelOptions(
            name='itemgroup',
            options={'ordering': ['title'], 'verbose_name_plural': 'Группы вещей'},
        ),
        migrations.AddField(
            model_name='catalogitem',
            name='catalog_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='group',
            field=models.ManyToManyField(blank=True, to='catalog.itemgroup'),
        ),
        migrations.CreateModel(
            name='CatalogGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Наименование каталога')),
                ('owners', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
