# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from datetime import timedelta
from os.path import abspath, dirname

from django.core.exceptions import ImproperlyConfigured

from luna_django_commons.settings import BaseSettings
from luna_django_commons.settings.mixins import CelerySettings


class SettingsBase(CelerySettings, BaseSettings):
    SETTINGS_DIR = abspath(dirname(__file__))

    PROJECT_BASENAME = 'pype'
    DEPLOYMENT_BASENAME = 'pype'

    # Required by cbs
    PROJECT_NAME = 'pype'

    def SECRET_KEY(self):
        return self.get_secret('SECRET_KEY')

    ALLOWED_HOSTS = [
        '127.0.0.1'
    ]

    TIME_ZONE = 'UTC'

    LANGUAGE_CODE = 'en'
    LANGUAGES = (('en', 'English'), )

    DEFAULT_FROM_EMAIL = 'noreply@pypeapp.com'

    SITE_ID = 1
    DOMAIN_NAME = 'dev.pypeapp.com'
    SITE_NAME = 'Pype (dev)'

    def STATICFILES_DIRS(self):
        return (
            self.root('static'),
            self.root('bower_components'),
        )

    LOGIN_REDIRECT_URL = '../../../virtualfolder/'
    LOGIN_URL = '/login/'

    MIDDLEWARE_CLASSES = (
        # Debreach content-length extension
        'debreach.middleware.RandomCommentMiddleware',

        # Django debug toolbar
        # 'debug_toolbar.middleware.DebugToolbarMiddleware',
        # 'silk.middleware.SilkyMiddleware',

        # Django-statsd
        'django_statsd.middleware.GraphiteRequestTimingMiddleware',
        'django_statsd.middleware.GraphiteMiddleware',

        # Debreach CSRF-token protection
        'debreach.middleware.CSRFCryptMiddleware',

        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',

        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        'django.middleware.locale.LocaleMiddleware',
    )

    @property
    def INSTALLED_APPS(self):
        installed_apps = super(SettingsBase, self).INSTALLED_APPS

        installed_apps += (
            'rest_framework',
            'rest_framework.authtoken',
            'djoser',
            'djng',
            'ui',
            'api',
            'luna_websockets',
        )

        return installed_apps

    # ----------------------------------------------------------------------------------------------------------------------
    # Rest framework settings
    REST_FRAMEWORK = {
        'PAGINATE_BY': 10,
        'DEFAULT_AUTHENTICATION_CLASSES': (
            # 'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.TokenAuthentication',

            # Session authentication is used in production
            'rest_framework.authentication.SessionAuthentication',
        ),
        'NON_FIELD_ERRORS_KEY': '__all__',
    }

    # Celery
    REDIS_DB_ID = '8'
    BROKER_URL = 'redis://localhost:6379/' + REDIS_DB_ID

    CELERYBEAT_SCHEDULE = {
    }

    # Intercom settings
    INTERCOM_APP_ID = "ems6rg8l"

    # Google Drive App Credentials
    def GOOGLE_DRIVE_CLIENT_ID(self):
        return None

    def GOOGLE_DRIVE_CLIENT_SECRET(self):
        return None

    def GOOGLE_DRIVE_CLIENT_URI(self):
        return None

    # Dropbox credentials
    def DROPBOX_APP_KEY(self):
        return None

    def DROPBOX_APP_SECRET(self):
        return None

    def DROPBOX_CLIENT_REDIRECT_URI(self):
        return None

    def JS_CONFIG(self):
        return {
            'DEBUG': self.DEBUG,
            'INTERCOM_APP_ID': None,
            'ENABLE_REGISTER': True,
            'WS_SERVER': 'http://127.0.0.1:22000/ws',
        }

    # DJOSER
    DJOSER = {
        'SET_PASSWORD_RETYPE': True,
        'PASSWORD_RESET_CONFIRM_URL': 'home/#/password/reset/{token}/{uid}/',
        'PASSWORD_RESET_CONFIRM_RETYPE': True,
    }
