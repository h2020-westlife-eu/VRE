# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20151126_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstorageaccount',
            name='name',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
