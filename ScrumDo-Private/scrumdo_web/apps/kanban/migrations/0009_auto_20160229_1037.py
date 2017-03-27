# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-29 10:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0008_auto_20160226_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedreport',
            name='aging_by',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='savedreport',
            name='aging_steps',
            field=models.CommaSeparatedIntegerField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='savedreport',
            name='aging_type',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='savedreport',
            name='tag',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]