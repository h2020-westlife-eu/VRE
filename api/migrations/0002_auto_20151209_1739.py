# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_squashed_0012_useraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='publish_key',
            field=models.CharField(default=b'', max_length=1024),
        ),
        migrations.AddField(
            model_name='dataset',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='datafile',
            name='storage_key',
            field=models.CharField(max_length=1024),
        ),
    ]
