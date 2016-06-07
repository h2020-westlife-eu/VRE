# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_datafile_upload_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='upload_state',
            field=models.CharField(default=b'DATAFILE_TRANSFER_IN_PROGRESS', max_length=255, choices=[(b'DATAFILE_READY', b'Ok'), (b'DATAFILE_UPLOAD_IN_PROGRESS', b'Upload in progress'), (b'DATAFILE_ERROR', b'Error'), (b'DATAFILE_TRANSFER_IN_PROGRESS', b'Transfer in progress')]),
        ),
    ]
