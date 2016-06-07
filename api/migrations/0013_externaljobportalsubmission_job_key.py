# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20160121_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='externaljobportalsubmission',
            name='job_key',
            field=models.CharField(max_length=1024, blank=True),
        ),
    ]
