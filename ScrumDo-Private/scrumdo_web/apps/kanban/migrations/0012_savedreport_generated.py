# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-04 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0011_savedreport_aging_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedreport',
            name='generated',
            field=models.BooleanField(default=False),
        ),
    ]
