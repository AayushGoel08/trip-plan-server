# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-29 16:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0022_trips_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='cities',
            name='defaulthome',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]