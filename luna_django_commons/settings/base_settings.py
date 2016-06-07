# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import json
import os.path

import cbs

from django.core.exceptions import ImproperlyConfigured

from luna_django_commons.settings.mixins import (
    AssetsSettings,
    DebugToolbarSettings,
    EmailSettings,
    StatsdSettings,
    TemplateSettings,
)


class BaseSettings(
    DebugToolbarSettings,
    StatsdSettings,
    AssetsSettings,
    EmailSettings,
    TemplateSettings,
    cbs.BaseSettings
):
    # Overrideable settings
    USE_SSL = False
    PRODUCTION = False
    DEBUG = True

    @property
    def PROJECT_BASENAME(self):
        raise ImproperlyConfigured('You must set PROJECT_BASENAME')

    @property
    def DEPLOYMENT_BASENAME(self):
        raise ImproperlyConfigured('You must set DEPLOYMENT_BASENAME')

    @property
    def BASE_URL(self):
        raise ImproperlyConfigured('You must set BASE_URL')

    @property
    def SETTINGS_DIR(self):
        raise ImproperlyConfigured('You must set SETTINGS_DIR')

    #
    # Helpers
    #
    def here(self, *dirs):
        return os.path.join(self.SETTINGS_DIR, *dirs)

    @property
    def BASE_DIR(self):
        return self.here('..', '..')

    def root(self, *dirs):
        return os.path.join(os.path.abspath(self.BASE_DIR), *dirs)

    _secrets = None

    def get_secret(self, setting):
        """ Get the secret variable or return explicit exception """

        if self._secrets is None:
            with open(self.here('secrets.json')) as f:
                self._secrets = json.loads(f.read())

        try:
            return self._secrets[setting]
        except KeyError:
            error_msg = "Set the {0} variable in secrets.json".format(setting)
            raise ImproperlyConfigured(error_msg)

    def LOGGING(self):
        if self.PRODUCTION:
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'json': {
                        '()': 'luna_django_commons.log.SysLogFormatter',
                    }
                },
                'filters': {
                    'require_debug_false': {
                        '()': 'django.utils.log.RequireDebugFalse'
                    },
                    'context_filter': {
                        '()': 'luna_django_commons.log.ContextFilter',
                        'DEPLOYMENT_BASENAME': self.DEPLOYMENT_BASENAME,
                    },
                    'celery_context_filter': {
                        '()': 'luna_django_commons.log.CeleryContextFilter',
                    }
                },
                'handlers': {
                    'null': {
                        'level': 'DEBUG',
                        'class': 'logging.NullHandler',
                    },
                    'mail_admins': {
                        'level': 'ERROR',
                        'filters': ['require_debug_false'],
                        'class': 'django.utils.log.AdminEmailHandler'
                    },
                    'syslog_json': {
                        'level': 'INFO',
                        'class': 'logging.handlers.SysLogHandler',
                        'formatter': 'json',
                        'address': '/dev/log',
                        'filters': ['context_filter', 'celery_context_filter']
                    }
                },
                'loggers': {
                    'django.request': {
                        'handlers': ['mail_admins', 'syslog_json'],
                        'level': 'DEBUG',
                        'propagate': False,
                    },
                    'django.security.DisallowedHost': {
                        'handlers': ['null'],
                        'propagate': False,
                    },
                    'django.security': {
                        'handlers': ['mail_admins', 'syslog_json'],
                        'level': 'DEBUG',
                        'propagate': False,
                    },
                    '': {
                        'handlers': ['syslog_json'],
                        'level': 'DEBUG',
                        'propagate': True,
                    }
                }
            }
        else:
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'verbose': {
                        'format': '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'level': 'INFO',
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                    }
                },
                'loggers': {
                    'django.request': {
                        'handlers': ['console'],
                        'level': 'DEBUG',
                        'propagate': True,
                    },
                    '': {
                        'handlers': ['console'],
                        'level': 'DEBUG',
                        'propagate': True,
                    }
                }
            }

    STATIC_URL = '/static/'
    ASSETS_URL = '/static/'

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    )

    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
        'django_assets.finders.AssetsFinder',
    )

    DB_NAME = None
    DB_USER = None
    DB_PASS = None
    DB_HOST = '127.0.0.1'
    DB_PORT = ''

    def DATABASES(self):
        if self.DB_NAME is None:
            raise ImproperlyConfigured('DB_NAME is not set')
        if self.DB_USER is None:
            self.DB_USER = self.DB_NAME
        if self.DB_PASS is None:
            self.DB_PASS = self.DB_NAME
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': self.DB_NAME,
                'USER': self.DB_USER,
                'PASSWORD': self.DB_PASS,
                'HOST': self.DB_HOST,
                'PORT': self.DB_PORT,
            }
        }

    ADMINS = []

    def MANAGERS(self):
        return self.ADMINS

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sitemaps',
        'django_assets',
        'django_statsd',
        'debreach',
        'debug_toolbar',
        'luna_django_commons.app',
    )

    def STATIC_ROOT(self):
        return self.root('static_prod/')

    def MEDIA_ROOT(self):
        return self.root('media/')

    def MEDIA_URL(self):
        return self.BASE_URL + '/media/'

    AUTHENTICATION_BACKENDS = (
#        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    def SESSION_COOKIE_SECURE(self):
        return self.USE_SSL

    def CSRF_COOKIE_SECURE(self):
        return self.USE_SSL
