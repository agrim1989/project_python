# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-04 06:00
from __future__ import unicode_literals

import apps.attachments.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attachments', '0002_attachment_story'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tmpattachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_file', models.FileField(max_length=512, upload_to=apps.attachments.models.attachment_attachment_upload, verbose_name='attachment')),
                ('attachment_url', models.CharField(max_length=512)),
                ('thumb_url', models.CharField(max_length=512)),
                ('attachment_type', models.CharField(choices=[(b'local', b'My Computer'), (b'dropbox', b'Dropbox')], default=b'local', max_length=15)),
                ('attachment_name', models.CharField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tmpattachments', to=settings.AUTH_USER_MODEL, verbose_name='tmpcreator')),
            ],
            options={
                'ordering': ['-created'],
                'db_table': 'v2_attachments_tmpattachment',
                'permissions': (('delete_foreign_attachments', 'Can delete foreign attachments'),),
            },
        ),
    ]
