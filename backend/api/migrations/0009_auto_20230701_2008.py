# Generated by Django 3.2 on 2023-07-01 17:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0008_auto_20230624_1855'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcart',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='shoppingcart',
            name='user',
        ),
        migrations.DeleteModel(
            name='Favorite',
        ),
        migrations.DeleteModel(
            name='ShoppingCart',
        ),
    ]