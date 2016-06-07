# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0009_dummyprovider'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('provider_name', models.CharField(max_length=1024)),
                ('username', models.CharField(max_length=1024)),
                ('password', models.CharField(max_length=1024)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalJobPortal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalJobPortalForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('template_name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalJobPortalFormGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=1024)),
                ('parent', models.ForeignKey(to='api.ExternalJobPortalFormGroup', null=True)),
                ('portal', models.ForeignKey(to='api.ExternalJobPortal')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalJobPortalSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('data', models.TextField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(to='api.ExternalJobPortal')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalJobPortalSubmissionStateChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(max_length=256, choices=[(b'EXTERNAL_SUBMISSION_RUNNING', b'Running'), (b'EXTERNAL_SUBMISSION_FAILED', b'FAILED'), (b'EXTERNAL_SUBMISSION_PENDING', b'Pending'), (b'EXTERNAL_SUBMISSION_PENDING_SUBMISSION', b'Submission in progress'), (b'EXTERNAL_SUBMISSION_SUCCESS', b'Succeeded')])),
                ('external_submission', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='externaljobportalform',
            name='parent',
            field=models.ForeignKey(to='api.ExternalJobPortalFormGroup', null=True),
        ),
        migrations.AddField(
            model_name='externaljobportalform',
            name='portal',
            field=models.ForeignKey(to='api.ExternalJobPortal'),
        ),
    ]
