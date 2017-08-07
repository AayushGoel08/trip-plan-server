# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-07 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0016_locations_hashtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='deposit',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trips',
            name='selections',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='trips',
            name='traversions',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='locations',
            name='price',
            field=models.CharField(max_length=500),
        ),
    ]
