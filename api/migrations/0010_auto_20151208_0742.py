# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_gdriveprovider_quota_bytes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='size',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
