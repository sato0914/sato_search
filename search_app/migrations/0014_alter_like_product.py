# Generated by Django 5.1.1 on 2024-12-04 06:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0013_rename_timestamp_like_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='search_app.product'),
        ),
    ]
