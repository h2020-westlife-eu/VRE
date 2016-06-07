# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20151217_1550'),
    ]

    operations = [
        migrations.CreateModel(
            name='B2DropProvider',
            fields=[
                ('userstorageaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='api.UserStorageAccount')),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
        ),
    ]
