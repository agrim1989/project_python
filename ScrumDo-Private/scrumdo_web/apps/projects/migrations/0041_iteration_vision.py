# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-04 03:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0040_iterationsentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteration',
            name='vision',
            field=models.TextField(blank=True, verbose_name=b'vision'),
        ),
    ]
