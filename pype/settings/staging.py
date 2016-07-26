# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from .base import SettingsBase


class SettingsStaging(SettingsBase):
    DEBUG = False
    PRODUCTION = True

    DEPLOYMENT_BASENAME = 'pype_staging'

    DB_NAME = 'pype_staging'

    ALLOWED_HOSTS = [
        'staging.pypeapp.com'
    ]

    BASE_URL = 'http://staging.pypeapp.com'
    MEDIA_ROOT = '/home/pype-staging/media/'

    ADMINS = (
        ('Matthieu Riviere', 'mriviere-symhub@leukensis.org'),
        ('Francois Ruty', 'fruty@luna-technology.com'),
        ('Adrien Brunet', 'abrunet@luna-technology.com'),
    )

    REDIS_DB_ID = '5'

    BROKER_URL = 'redis://localhost:6379/' + REDIS_DB_ID

    def JS_CONFIG(self):
        conf = super(SettingsStaging, self).JS_CONFIG()
        conf['WS_SERVER'] = self.BASE_URL + '/ws'
        return conf
