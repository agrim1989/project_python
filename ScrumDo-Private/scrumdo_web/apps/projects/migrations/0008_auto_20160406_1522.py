# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-06 15:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='folder_item_name',
            field=models.CharField(default=b'Epic', max_length=32),
        ),
        migrations.AddField(
            model_name='project',
            name='work_item_name',
            field=models.CharField(default=b'Card', max_length=32),
        ),
        migrations.AlterField(
            model_name='project',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='projects.Project'),
        ),
    ]
