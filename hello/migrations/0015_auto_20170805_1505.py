# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-05 09:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0014_auto_20170805_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locstore',
            name='deposit',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='locstore',
            name='price',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='locstore',
            name='time',
            field=models.CharField(max_length=500),
        ),
    ]