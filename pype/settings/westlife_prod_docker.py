# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

from .base import SettingsBase
import os
import sys


class SettingsWestLifeProdDocker(SettingsBase):
    DEBUG = False
    PRODUCTION = True
    USE_SSL = True

    DEPLOYMENT_BASENAME = 'pype_westlife_prod'

    DB_NAME = os.getenv('POSTGRESQL_DB', 'pype_westlife_prod')
    DB_USER = os.getenv('POSTGRESQL_USER', 'pype_westlife_prod')
    DB_PASS = os.getenv('POSTGRESQL_PASS', 'pype_westlife_prod')

    ALLOWED_HOSTS = [
        'admin.west-life.eu',
        'www.west-life.eu',
        'portal.west-life.eu',
    ]

    BASE_URL = 'https://portal.west-life.eu'
    MEDIA_ROOT = '/home/pype-westlife-prod/media/'

    @property
    def INSTALLED_APPS(self):
        installed_apps = super(SettingsWestLifeProdDocker, self).INSTALLED_APPS

        installed_apps += (
            'djangosaml2',
        )

        return installed_apps

    ADMINS = (
    )

    REDIS_DB_ID = '0'

    BROKER_URL = 'redis://redis:6379/' + REDIS_DB_ID

    def JS_CONFIG(self):
        conf = super(SettingsWestLifeProdDocker, self).JS_CONFIG()
        conf['ENABLE_REGISTER'] = True
        conf['WS_SERVER'] = self.BASE_URL + '/ws'
        return conf

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'djangosaml2.backends.Saml2Backend',
    )

    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    LOGGING = {
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
                'DEPLOYMENT_BASENAME': 'pype_westlife_prod'
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
            'stdout': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'json',
                'filters': ['context_filter', 'celery_context_filter']
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins', 'stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django.security.DisallowedHost': {
                'handlers': ['null'],
                'propagate': False,
            },
            'django.security': {
                'handlers': ['mail_admins', 'stdout'],
                'level': 'DEBUG',
                'propagate': False,
            },
            '': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': True,
            }
        }
    }


    import os.path
    import saml2
    import saml2.saml

    CURDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
    SAML_CONFIG = {
        'xmlsec_binary': '/usr/bin/xmlsec1',

        'entityid': 'https://portal.west-life.eu/saml2/metadata/',

        'attribute_map_dir': os.path.join(CURDIR, 'attribute-maps'),

        'service': {
            'sp': {
                'name': 'West-Life VRE Portal',
                'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,
                # 'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
                'endpoints': {
                    'assertion_consumer_service': [
                        ('https://portal.west-life.eu/saml2/acs/',
                         saml2.BINDING_HTTP_POST),
                    ],

                    'single_logout_service': [
                        ('https://portal.west-life.eu/saml2/ls/',
                         saml2.BINDING_HTTP_REDIRECT),
                        ('https://portal.west-life.eu/saml2/ls/post',
                         saml2.BINDING_HTTP_POST),
                    ],
                },

                "authn_requests_signed": True,
                'allow_unsolicited': True,

                'required_attributes': ['uid', 'mail', 'cn', 'sn'],

                'optional_attributes': ['uid', 'email', 'eduPersonAffiliation'],
            },
        },

        'metadata': {
            'local': [os.path.join(CURDIR, 'instruct-providers.xml')],
        },

        'debug': 1,

        'key_file': os.path.join(CURDIR, 'shib-prod-instruct.key'),
        'cert_file': os.path.join(CURDIR, 'shib-prod-instruct.pem'),

        'encryption_keypairs': [
            {
                'key_file': os.path.join(CURDIR, 'shib-prod-instruct.key'),
                'cert_file': os.path.join(CURDIR, 'shib-prod-instruct.pem'),
            }
        ],

        'contact_person': [
            {
                'given_name': 'Matthieu',
                'sur_name': 'Riviere',
                'company': 'Luna',
                'email_address': 'mriviere@luna-technology.com',
                'contact_type': 'technical'
            },
            {
                'given_name': 'Matthieu',
                'sur_name': 'Riviere',
                'company': 'Luna',
                'email_address': 'mriviere@luna-technology.com',
                'contact_type': 'administrative'
            }
        ],
        'organization': {
            'name': [
                ('West-Life', 'en')
            ],
            'display_name': [
                ('West-Life', 'en')
            ],
            'url': [
                ('https://portal.west-life.eu', 'en')
            ]
        }
    }

    SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'

    SAML_ATTRIBUTE_MAPPING = {
        # 'displayName': ('username',),
        'mail': ('email', 'username')
        # 'givenName': ('first_name',),
        # 'sn': ('last_name',),
    }
