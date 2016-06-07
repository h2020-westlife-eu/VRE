# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20151208_0742'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='external_link',
            field=models.URLField(max_length=8192, blank=True),
        ),
    ]
