# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20151130_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='storage_key',
            field=models.CharField(default='root', max_length=1024),
            preserve_default=False,
        ),
    ]
