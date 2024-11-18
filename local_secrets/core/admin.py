import logging

from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from nested_admin import nested
from oauth2_provider.admin import AccessTokenAdmin, ApplicationAdmin, RefreshTokenAdmin
from oauth2_provider.models import AccessToken, Application, RefreshToken

from local_secrets.users.models import GroupDescription, TranslatedGroupDescription

project_name = f'{settings.PROJECT_NAME.format(settings.ENVIRONMENT)}'
logger = logging.getLogger(__name__)


class MyAdminSite(AdminSite):
    site_title = site_header = project_name

    default_order = 100
    ordering = {
        'app_version': 100,
        'auth': 100,
        'oauth2_provider': 100,
        'sites': 0,
        'events': 10,
        'searches': 11,
        'operations': 12,
        'travels': 20,
        'routes': 30,
        'cities': 40,
        'languages': 50,
        'users': 99,
    }

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)

        app_list = sorted(app_dict.values(), key=self.sorting_dict())

        return app_list

    def sorting_dict(self):
        ordering = self.ordering
        default_order = self.default_order

        def sort_lambda(app_module):
            app_key = app_module['app_label']
            if app_key not in ordering:
                logger.warning(
                    f"App [{app_key}] not found in admin ordering dict, so default value is assigned "
                    f"({default_order})"
                )
            return ordering.get(app_key, default_order)

        return sort_lambda


class TranslatedGroupDescriptionInline(nested.NestedStackedInline):
    model = TranslatedGroupDescription
    extra = 0


class GroupDescriptionInline(nested.NestedStackedInline):
    model = GroupDescription
    extra = 0

    inlines = [
        TranslatedGroupDescriptionInline,
    ]


class CustomGroupAdmin(GroupAdmin, nested.NestedModelAdmin):
    inlines = [
        GroupDescriptionInline,
    ]


admin_site = MyAdminSite(name=project_name)


# Default user admin
admin_site.register(Group, CustomGroupAdmin)

# OAuth admin
admin_site.register(Application, ApplicationAdmin)
admin_site.register(AccessToken, AccessTokenAdmin)
admin_site.register(RefreshToken, RefreshTokenAdmin)
