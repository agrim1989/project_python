# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-13 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0055_auto_20170202_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliolevel',
            name='work_item_name',
            field=models.CharField(default=b'Card', max_length=32),
        ),
    ]
