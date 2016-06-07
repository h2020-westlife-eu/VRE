# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_dropboxprovider'),
    ]

    operations = [
        migrations.CreateModel(
            name='DummyProvider',
            fields=[
                ('userstorageaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='api.UserStorageAccount')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
        ),
    ]
