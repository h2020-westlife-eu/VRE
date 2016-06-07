# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_userstorageaccount_validated'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncOperation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='userstorageaccount',
            name='validation_state',
            field=models.CharField(default=b'STORAGE_ACCOUNT_PENDING_VALIDATION', max_length=255, choices=[(b'STORAGE_ACCOUNT_PENDING_VALIDATION', b'Pending validation'), (b'STORAGE_ACCOUNT_READY', b'Ready'), (b'STORAGE_ACCOUNT_VALIDATING', b'Validation in progress'), (b'STORAGE_ACCOUNT_VALIDATION_FAILED', b'Validation failed')]),
        ),
        migrations.AddField(
            model_name='syncoperation',
            name='storage_account',
            field=models.ForeignKey(to='api.UserStorageAccount'),
        ),
    ]
