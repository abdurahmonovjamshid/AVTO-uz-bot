# Generated by Django 4.2.4 on 2023-09-24 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0010_alter_car_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='telegram_id',
            field=models.BigIntegerField(unique=True),
        ),
    ]
