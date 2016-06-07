# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_b2dropprovider'),
    ]

    operations = [
        migrations.CreateModel(
            name='DropboxProvider',
            fields=[
                ('userstorageaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='api.UserStorageAccount')),
                ('access_user_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('quota_bytes', models.BigIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
        ),
    ]
