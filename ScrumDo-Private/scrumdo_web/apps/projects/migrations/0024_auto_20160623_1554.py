# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-23 15:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='root',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='projects.Project'),
        ),
        migrations.AlterField(
            model_name='portfoliolevel',
            name='projects',
            field=models.ManyToManyField(related_name='portfolio', to='projects.Project'),
        ),
    ]
