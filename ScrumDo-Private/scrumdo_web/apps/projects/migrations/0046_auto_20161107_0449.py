# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-07 04:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0045_project_tab_timeline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='risk',
            name='iterations',
            field=models.ManyToManyField(related_name='risks', to='projects.Iteration'),
        ),
        migrations.AlterField(
            model_name='risk',
            name='projects',
            field=models.ManyToManyField(related_name='risks', to='projects.Project'),
        ),
    ]
