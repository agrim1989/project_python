# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-12 10:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classic', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='backloghistorysnapshot',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='backloghistorystories',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='basecampetags',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='boardattributes',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='boardcell',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='boardgraphic',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='boardheader',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='boardimage',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='cellmovement',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='commit',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='epic',
            options={'managed': False, 'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='externalstorymapping',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='externaltaskmapping',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='extraconfiguration',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='githubbinding',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='githubcredentials',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='githublog',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='iteration',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='kanbanstat',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='newsitem',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pointslog',
            options={'managed': False, 'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='policy',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='policyage',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'managed': False, 'ordering': ['-active', 'name']},
        ),
        migrations.AlterModelOptions(
            name='projectextramapping',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='stepmovement',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='stepstat',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='story',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='storyattributes',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='storymentions',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='storyqueue',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='storytag',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='storytagging',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='syncronizationqueue',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='tasktagging',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='teamproject',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='timeentry',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='workflow',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='workflowstep',
            options={'managed': False},
        ),
    ]
