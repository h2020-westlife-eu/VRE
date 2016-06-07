# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'api', '0001_initial'), (b'api', '0002_auto_20151123_1606'), (b'api', '0003_auto_20151125_1435'), (b'api', '0004_datafile_upload_state'), (b'api', '0005_auto_20151126_0153'), (b'api', '0006_userstorageaccount_name'), (b'api', '0007_auto_20151130_2059'), (b'api', '0008_folder_storage_key'), (b'api', '0009_gdriveprovider_quota_bytes'), (b'api', '0010_auto_20151208_0742'), (b'api', '0011_datafile_external_link'), (b'api', '0012_useraction')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Datafile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('filename', models.CharField(max_length=1024)),
                ('size', models.IntegerField(default=0)),
                ('storage_key', models.CharField(default='', max_length=1024)),
                ('upload_state', models.CharField(default=b'DATAFILE_TRANSFER_IN_PROGRESS', max_length=255, choices=[(b'DATAFILE_READY', b'Ok'), (b'DATAFILE_UPLOAD_IN_PROGRESS', b'Upload in progress'), (b'DATAFILE_ERROR', b'Error'), (b'DATAFILE_TRANSFER_IN_PROGRESS', b'Transfer in progress')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserStorageAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='S3Provider',
            fields=[
                ('userstorageaccount_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='api.UserStorageAccount')),
                ('access_key_id', models.CharField(max_length=255)),
                ('secret_access_key', models.CharField(max_length=255)),
                ('bucket_name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
        ),
        migrations.AddField(
            model_name='userstorageaccount',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userstorageaccount',
            name='validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userstorageaccount',
            name='name',
            field=models.CharField(max_length=255, blank=True),
        ),
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
                ('quota_bytes', models.BigIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=('api.userstorageaccount',),
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
        migrations.AddField(
            model_name='folder',
            name='storage_key',
            field=models.CharField(default='root', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datafile',
            name='size',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='datafile',
            name='external_link',
            field=models.URLField(max_length=8192, blank=True),
        ),
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('action_type', models.CharField(max_length=255)),
                ('args', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
