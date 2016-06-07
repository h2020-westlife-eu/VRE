# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20151123_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='file',
        ),
        migrations.AddField(
            model_name='datafile',
            name='size',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='datafile',
            name='storage_account',
            field=models.ForeignKey(default=None, to='api.UserStorageAccount'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datafile',
            name='storage_key',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userstorageaccount',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]
