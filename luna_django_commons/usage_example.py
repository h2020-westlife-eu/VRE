# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>


from django_luna_base import populate_settings

# ...
# Some project-specific settings here
# ...

USE_SSL = True
LOG_DIRECTORY = '/home/swarmhq-prod/logs/'
PRODUCTION = True
CANONICAL_URL = 'https://www.swarmhq.com/'
PROJECT_BASENAME = 'swarmhq'

# globals() contains all the module-level variables. We pass it to populate_settings(),
# so it can access what we already defined, modify it, and add new values
populate_settings(globals())

# ...
# Some project-specific settings overriding the default ones here
# ...

ALLOWED_HOSTS = [
    'future.codecairn.com',
    'future.symhub.com',
]
