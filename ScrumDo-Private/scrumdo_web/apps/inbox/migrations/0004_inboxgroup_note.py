# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-28 04:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0027_note_active'),
        ('inbox', '0003_auto_20160209_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboxgroup',
            name='note',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Note'),
        ),
    ]
