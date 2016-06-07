# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20160121_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaljobportalsubmissionstatechange',
            name='external_submission',
            field=models.ForeignKey(to='api.ExternalJobPortalSubmission'),
        ),
    ]
