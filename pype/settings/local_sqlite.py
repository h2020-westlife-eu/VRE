# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


from .base import SettingsBase


class SettingsLocalSqlite(SettingsBase):
    DEBUG = True

    BASE_URL = 'http://127.0.0.1:8004'

    def JS_CONFIG(self):
        conf = super(SettingsLocalSqlite, self).JS_CONFIG()
        conf['WS_SERVER'] = 'http://127.0.0.1:22000/ws'
        conf['ENABLE_REGISTER'] = True
        return conf

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'sqlite.db'
        }
    }
