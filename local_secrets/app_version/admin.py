from .models import AppVersion, Store, UserAppVersion
from ..core.admin import admin_site

admin_site.register(AppVersion)
admin_site.register(UserAppVersion)
admin_site.register(Store)
