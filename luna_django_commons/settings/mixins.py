# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


class DebugToolbarSettings(object):
    INTERNAL_IPS = [
        '127.0.0.1',
        '192.168.56.1',
    ]

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

    DEBUG_TOOLBAR_REQUEST_HISTORY_ENABLE = False

    def DEBUG_TOOLBAR_PANELS(self):
        r = [
            'debug_toolbar.panels.versions.VersionsPanel',
            'debug_toolbar.panels.timer.TimerPanel',
            'debug_toolbar.panels.settings.SettingsPanel',
            'debug_toolbar.panels.headers.HeadersPanel',
            'debug_toolbar.panels.request.RequestPanel',
            'debug_toolbar.panels.sql.SQLPanel',
            'debug_toolbar.panels.staticfiles.StaticFilesPanel',
            'debug_toolbar.panels.templates.TemplatesPanel',
            'debug_toolbar.panels.cache.CachePanel',
            'debug_toolbar.panels.signals.SignalsPanel',
            'debug_toolbar.panels.logging.LoggingPanel',
            'debug_toolbar.panels.redirects.RedirectsPanel',
            'django_statsd.panel.StatsdPanel',
        ]

        if self.DEBUG_TOOLBAR_REQUEST_HISTORY_ENABLE:
            r += [
                'ddt_request_history.panels.request_history.RequestHistoryPanel',
            ]

        return r

    def DEBUG_TOOLBAR_CONFIG(self):
        if self.DEBUG_TOOLBAR_REQUEST_HISTORY_ENABLE:
            return {
                'SHOW_TOOLBAR_CALLBACK': 'ddt_request_history.panels.request_history.allow_ajax',
                'RESULTS_STORE_SIZE': 100,
            }
        else:
            return {}


class StatsdSettings(object):
    STATSD_HOST = '10.63.90.58'
    STATSD_PORT = 8125

    def STATSD_PREFIX(self):
        return self.DEPLOYMENT_BASENAME

    STATSD_MAXUDPSIZE = 512

    def STATSD_CLIENT(self):
        if self.PRODUCTION:
            return 'django_statsd.clients.normal'
        else:
            return 'django_statsd.clients.toolbar'

    STATSD_PATCHES = [
        'django_statsd.patches.db'
    ]

    STATSD_MODEL_SIGNALS = True

    def TOOLBAR_STATSD(self):
        return {
            'graphite': 'http://nagios.luna:15433/render/',
            'roots': {
                'timers': [
                    'stats.timers.%s_staging' % self.PROJECT_BASENAME,
                    'stats.timers.%s_prod' % self.PROJECT_BASENAME,
                ],
                'counts': [
                    'stats.%s_staging' % self.PROJECT_BASENAME,
                    'stats.%s_prod' % self.PROJECT_BASENAME,
                ]
            }
        }


class TemplateSettings(object):

    def TEMPLATES(self):

        return [{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates'],  # I think that's the default config anyway
            'OPTIONS': {
                'context_processors': self._TEMPLATE_CONTEXT_PROCESSORS,
                'loaders': self._TEMPLATE_LOADERS()
            },
        }, ]

    def _TEMPLATE_LOADERS(self):
        loaders = (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            # 'django.template.loaders.eggs.Loader',
        )

        # If DEBUG is False, enable template caching
        if self.DEBUG:
            return loaders
        else:
            return (
                ('django.template.loaders.cached.Loader', loaders),
            )

    _TEMPLATE_CONTEXT_PROCESSORS = (
        'debreach.context_processors.csrf',
        'django.contrib.auth.context_processors.auth',
        'django.template.context_processors.debug',
        'django.template.context_processors.i18n',
        'django.template.context_processors.media',
        'django.template.context_processors.request',
        'django.template.context_processors.static',
        'django.template.context_processors.tz',
        'django.contrib.messages.context_processors.messages',
    )




class AssetsSettings(object):
    ASSETS_VERSIONS = 'hash:32'
    # The javascript we have doesn't pass with Closure advanced optimizations
    # CLOSURE_COMPRESSOR_OPTIMIZATION = 'ADVANCED_OPTIMIZATIONS'

    CLOSURE_EXTRA_ARGS = ['--language_in', 'ECMASCRIPT5']

    ASSETS_URL_EXPIRE = False

    def ASSETS_DEBUG(self):
        return self.DEBUG

    def ASSETS_AUTO_BUILD(self):
        return self.DEBUG


class EmailSettings(object):
    def EMAIL_BACKEND(self):
        if self.PRODUCTION:
            return 'django.core.mail.backends.smtp.EmailBackend'
        else:
            return 'django.core.mail.backends.console.EmailBackend'

    def EMAIL_HOST(self):
        if self.PRODUCTION:
            return 'in-v3.mailjet.com'
        else:
            return None

    def EMAIL_PORT(self):
        if self.PRODUCTION:
            return 587
        else:
            return None

    def EMAIL_HOST_USER(self):
        if self.PRODUCTION:
            return self.get_secret('MAILJET_USERNAME')
        else:
            return None

    def EMAIL_HOST_PASSWORD(self):
        if self.PRODUCTION:
            return self.get_secret('MAILJET_PASSWORD')
        else:
            return None

    EMAIL_USE_TLS = True

    def SERVER_EMAIL(self):
        return self.DEFAULT_FROM_EMAIL


class CelerySettings(object):
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_SEND_TASK_ERROR_EMAILS = True

    def CELERY_RESULT_BACKEND(self):
        return self.BROKER_URL
