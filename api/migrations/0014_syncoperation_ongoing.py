# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_externaljobportalsubmission_job_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncoperation',
            name='ongoing',
            field=models.BooleanField(default=False),
        ),
    ]
