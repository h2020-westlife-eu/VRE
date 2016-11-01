# Import all the possible settings classes so they are in globals() and apply_settings can see them
from .dev import SettingsDev
from .jenkins import SettingsJenkins
from .local_sqlite import SettingsLocalSqlite
from .staging import SettingsStaging
from .westlife_prod import SettingsWestLifeProd

from luna_django_commons.settings import apply_settings

apply_settings(globals())

#
# Post-settings actions
#
