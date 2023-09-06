# Generated by Django 4.2.4 on 2023-09-06 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_car_dislikes_car_likes_car_seen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='car',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='car',
            name='seen',
        ),
        migrations.AddField(
            model_name='car',
            name='dislikes',
            field=models.ManyToManyField(related_name='disliked_cars', to='bot.tguser'),
        ),
        migrations.AddField(
            model_name='car',
            name='likes',
            field=models.ManyToManyField(related_name='liked_cars', to='bot.tguser'),
        ),
        migrations.AddField(
            model_name='car',
            name='seen',
            field=models.ManyToManyField(related_name='seen_cars', to='bot.tguser'),
        ),
    ]
