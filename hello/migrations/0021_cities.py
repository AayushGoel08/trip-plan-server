# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-16 06:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0020_trips_paysum'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100)),
                ('cityid', models.CharField(max_length=100)),
            ],
        ),
    ]