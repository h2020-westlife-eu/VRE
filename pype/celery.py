# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from __future__ import absolute_import

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pype.settings')

from django.conf import settings
from celery.signals import setup_logging

@setup_logging.connect
def configure_logging(sender=None, **kwargs):
    import logging
    import logging.config
    logging.config.dictConfig(settings.LOGGING)

app = Celery('pype')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
