# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-11 17:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0004_locations'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='locid',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
    ]
