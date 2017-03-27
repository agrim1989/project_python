# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0013_auto_20160511_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellmovement',
            name='points_value',
            field=models.DecimalField(decimal_places=1, max_digits=8),
        ),
        migrations.AlterField(
            model_name='tagmovement',
            name='points_value',
            field=models.DecimalField(decimal_places=1, default=b'0.0', max_digits=8),
        ),
    ]
