# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-24 14:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0025_auto_20160624_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfoliolevel',
            name='projects',
        ),
        migrations.AddField(
            model_name='project',
            name='portfolio_level',
            field=models.ForeignKey(default=None, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='projects', to='projects.PortfolioLevel'),
        ),
    ]