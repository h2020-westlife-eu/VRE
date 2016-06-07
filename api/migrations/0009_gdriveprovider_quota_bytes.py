# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_folder_storage_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='gdriveprovider',
            name='quota_bytes',
            field=models.BigIntegerField(default=0),
        ),
    ]
