# Generated by Django 4.2.4 on 2023-09-06 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_search_complate'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='car',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='car',
            name='seen',
            field=models.IntegerField(default=0),
        ),
    ]
