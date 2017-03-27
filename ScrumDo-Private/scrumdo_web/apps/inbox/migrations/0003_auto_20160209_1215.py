# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20160113_1204'),
        ('inbox', '0002_auto_20160115_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboxgroup',
            name='epic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Epic'),
        ),
        migrations.AlterField(
            model_name='inboxentry',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='inbox.InboxGroup'),
        ),
    ]
