# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from .base import SettingsBase


class SettingsWestLifeProd(SettingsBase):
    DEBUG = False
    PRODUCTION = True
    USE_SSL = True

    DEPLOYMENT_BASENAME = 'pype_westlife_prod'

    DB_NAME = 'pype_westlife_prod'
    DB_USER = 'pype_westlife_prod'
    DB_PASS = 'pype_westlife_prod'

    ALLOWED_HOSTS = [
        'admin.west-life.eu',
        'www.west-life.eu',
        'portal.west-life.eu',
    ]

    BASE_URL = 'https://portal.west-life.eu'
    MEDIA_ROOT = '/home/pype-westlife-prod/media/'

    ADMINS = (
    )

    REDIS_DB_ID = '0'

    BROKER_URL = 'redis://localhost:6379/' + REDIS_DB_ID

    def JS_CONFIG(self):
        conf = super(SettingsWestLifeProd, self).JS_CONFIG()
        conf['ENABLE_REGISTER'] = True
        conf['WS_SERVER'] = self.BASE_URL + '/ws'
        return conf

