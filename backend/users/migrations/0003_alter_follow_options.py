# Generated by Django 3.2 on 2023-06-19 20:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_auto_20230619_2208'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-created',)},
        ),
    ]
