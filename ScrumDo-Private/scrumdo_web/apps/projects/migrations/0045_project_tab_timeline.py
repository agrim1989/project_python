# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-10-13 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0044_project_tab_milestones'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='tab_timeline',
            field=models.BooleanField(default=True),
        ),
    ]
