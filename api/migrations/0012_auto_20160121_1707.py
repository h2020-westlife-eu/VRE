# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20160121_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='externaljobportalform',
            name='original_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='externaljobportalform',
            name='submit_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='externaljobportalsubmission',
            name='target',
            field=models.ForeignKey(to='api.ExternalJobPortalForm'),
        ),
    ]
