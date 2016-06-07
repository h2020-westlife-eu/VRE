# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_userstorageaccount_validation_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userstorageaccount',
            name='validated',
        ),
    ]
