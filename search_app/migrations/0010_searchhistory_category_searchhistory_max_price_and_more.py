# Generated by Django 5.1.1 on 2024-11-18 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0009_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchhistory',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='searchhistory',
            name='max_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Max Price'),
        ),
        migrations.AddField(
            model_name='searchhistory',
            name='min_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Min Price'),
        ),
        migrations.AddField(
            model_name='searchhistory',
            name='sort',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Sort Order'),
        ),
    ]
