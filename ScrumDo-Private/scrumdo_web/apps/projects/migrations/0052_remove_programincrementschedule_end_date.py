# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-29 02:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0051_auto_20161220_0641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programincrementschedule',
            name='end_date',
        ),
    ]
