# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-02 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_auto_20161102_0353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='caption',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
