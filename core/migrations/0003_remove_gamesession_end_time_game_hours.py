# Generated by Django 4.2.20 on 2025-06-27 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_game_vip_price_remove_gamesession_tariff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesession',
            name='end_time',
        ),
        migrations.AddField(
            model_name='game',
            name='hours',
            field=models.PositiveIntegerField(default=1, verbose_name='O‘yin davomiyligi (soat)'),
        ),
    ]
