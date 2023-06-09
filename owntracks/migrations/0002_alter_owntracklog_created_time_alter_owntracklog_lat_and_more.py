# Generated by Django 4.1.3 on 2022-12-20 10:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('owntracks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='owntracklog',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='creation time'),
        ),
        migrations.AlterField(
            model_name='owntracklog',
            name='lat',
            field=models.FloatField(verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='owntracklog',
            name='lon',
            field=models.FloatField(verbose_name='longitude'),
        ),
        migrations.AlterField(
            model_name='owntracklog',
            name='tid',
            field=models.CharField(max_length=100, verbose_name='user'),
        ),
    ]
