# Generated by Django 5.2.3 on 2025-06-20 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_inventoryadjustment'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='current_stock',
            field=models.IntegerField(default=0),
        ),
    ]
