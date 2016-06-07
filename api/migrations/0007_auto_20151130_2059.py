# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_userstorageaccount_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(to='api.Folder', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GDriveProvider',
            fields=[
                ('userstorageaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='api.UserStorageAccount')),
                ('credentials', models.CharField(max_length=4096)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
        ),
        migrations.RenameField(
            model_name='datafile',
            old_name='path',
            new_name='filename',
        ),
        migrations.RemoveField(
            model_name='datafile',
            name='dataset',
        ),
        migrations.RemoveField(
            model_name='datafile',
            name='storage_account',
        ),
        migrations.AddField(
            model_name='datafile',
            name='owner',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='storage_account',
            field=models.ForeignKey(to='api.UserStorageAccount'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='folder',
            field=models.ForeignKey(default=0, to='api.Folder'),
            preserve_default=False,
        ),
    ]
