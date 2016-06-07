# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20151209_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstorageaccount',
            name='validation_state',
            field=models.CharField(default=b'STORAGE_ACCOUNT_PENDING_VALIDATION', max_length=255, choices=[(b'STORAGE_ACCOUNT_PENDING_VALIDATION', b'Pending validation'), (b'STORAGE_ACCOUNT_VALIDATING', b'Ready'), (b'STORAGE_ACCOUNT_VALIDATION_FAILED', b'Validation failed')]),
        ),
    ]
