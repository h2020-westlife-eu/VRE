# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20151125_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='upload_state',
            field=models.CharField(default=b'UPLOAD_STATE_PENDING', max_length=255),
        ),
    ]
