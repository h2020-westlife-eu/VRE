# coding: utf-8

# Copyright Luna Technology 2015

from .base import SettingsBase


class SettingsDev(SettingsBase):
    DEBUG = True

    DB_NAME = 'pype'
    DB_USER = 'pype'
    DB_PASS = 'pype'

    BASE_URL = 'http://192.168.56.102:8000'

    @property
    def INSTALLED_APPS(self):
        installed_apps = super(SettingsDev, self).INSTALLED_APPS

        installed_apps += (
            'djangosaml2',
        )

        return installed_apps

    def JS_CONFIG(self):
        conf = super(SettingsDev, self).JS_CONFIG()
        conf['WS_SERVER'] = 'http://192.168.56.102:22000/ws'
        conf['ENABLE_REGISTER'] = True
        return conf

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'djangosaml2.backends.Saml2Backend',
    )

    LOGIN_URL = '/saml2/login/'
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    import os.path
    import saml2
    import saml2.saml
    CURDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saml')
    SAML_CONFIG = {
        'xmlsec_binary': '/usr/bin/xmlsec1',

        'entityid': 'http://10.81.73.65:8004/saml2/metadata/',

        'attribute_map_dir': os.path.join(CURDIR, 'attribute-maps'),

        'service': {
            'sp': {
                'name': 'Federated Django sample SP',
                'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,
                #'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
                'endpoints': {
                    'assertion_consumer_service': [
                        ('http://10.81.73.65:8004/saml2/acs/',
                         saml2.BINDING_HTTP_POST),
                    ],

                    'single_logout_service': [
                        ('http://10.81.73.65:8004/saml2/ls/',
                         saml2.BINDING_HTTP_REDIRECT),
                        ('http://10.81.73.65:8004/saml2/ls/post',
                         saml2.BINDING_HTTP_POST),
                    ],
                },

                "authn_requests_signed": True,
                'allow_unsolicited': True,

                'required_attributes': ['uid', 'mail', 'cn', 'sn'],

                'optional_attributes': ['uid', 'email', 'eduPersonAffiliation'],

                # 'idp': {
                #     'https://localhost/simplesaml/saml2/idp/metadata.php': {
                #         'single_sign_on_service': {
                #             saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SSOService.php',
                #         },
                #         'single_logout_service': {
                #             saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                #         },
                #     },
                # }
                # 'idp': {
                #     'http://www.testshib.org/metadata/testshib-providers.xml': {
                #         'single_sign_on_service': {
                #             saml2.BINDING_HTTP_REDIRECT: 'https://idp.testshib.org/idp/profile/SAML2/Redirect/SSO',
                #         },
                #         # 'single_logout_service': {
                #         #     saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                #         # },
                #     },
                # }
            },
        },

        'metadata': {
            'local': [os.path.join(CURDIR, 'testshib-providers.xml')],
        },

        'debug': 1,

        'key_file': os.path.join(CURDIR, 'shib-test-2.key'),
        'cert_file': os.path.join(CURDIR, 'shib-test-2.pem'),

        'encryption_keypairs': [
            {
                'key_file': os.path.join(CURDIR, 'shib-test-2.key'),
                'cert_file': os.path.join(CURDIR, 'shib-test-2.pem'),
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
                ('https://www.west-life.eu', 'en')
            ]
        },
        'valid_for': 24
    }

    SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'username'

    SAML_ATTRIBUTE_MAPPING = {
        'uid': ('username',),
        'mail': ('email',),
        'givenName': ('first_name',),
        'sn': ('last_name',),
    }