# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-28 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0015_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='kanbanstat',
            name='lead_time_65',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='kanbanstat',
            name='lead_time_85',
            field=models.IntegerField(default=0),
        ),
    ]