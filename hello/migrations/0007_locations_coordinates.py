# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-14 08:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0006_auto_20170713_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='coordinates',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
