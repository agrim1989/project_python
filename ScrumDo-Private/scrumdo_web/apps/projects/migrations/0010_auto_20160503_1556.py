# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 15:22
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Count

import logging

logger = logging.getLogger(__name__)

def remove_duplicates(apps, schema_editor):
    PR = apps.get_model("projects", "PullRequest")
    for c in PR.objects.values("link").annotate(Count("id")).order_by("link").filter(id__count__gt=1):
        todelete = PR.objects.filter(link=c['link']).order_by("-state")[1:]
        for pr in todelete:
            pr.delete()
            logger.info(pr)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20160503_1441'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates),
        migrations.AlterField(
            model_name='pullrequest',
            name='link',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]