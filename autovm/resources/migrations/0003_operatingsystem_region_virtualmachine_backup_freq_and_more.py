# Generated by Django 5.0.9 on 2024-09-09 14:26

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0002_remove_virtualmachine_is_deleted_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OperatingSystem",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="backup_freq",
            field=models.CharField(
                choices=[
                    ("daily", "Daily"),
                    ("weekly", "Weekly"),
                    ("monthly", "Monthly"),
                ],
                default="daily",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="virtualmachine",
            name="description",
            field=models.TextField(blank=True, help_text="Human readable description"),
        ),
        migrations.AlterField(
            model_name="virtualmachine",
            name="disk_size",
            field=models.CharField(
                choices=[
                    ("200", "200 GB SSD"),
                    ("300", "300 GB SSD"),
                    ("400", "400 GB SSD"),
                    ("600", "600 GB SSD"),
                    ("1000", "1 TB SSD"),
                ],
                default="200",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="OperatingSystemVersion",
            fields=[
                (
                    "_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("version", models.CharField(max_length=20)),
                (
                    "operating_system",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="resources.operatingsystem",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="operating_system_version",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="resources.operatingsystemversion",
            ),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="region",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="resources.region",
            ),
        ),
    ]
