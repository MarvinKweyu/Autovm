# Generated by Django 5.1.1 on 2024-09-19 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0007_region_slug_alter_region_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notification",
            options={"ordering": ["-created"]},
        ),
    ]
