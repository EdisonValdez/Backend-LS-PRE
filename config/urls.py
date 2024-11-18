"""local-secrets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

from local_secrets.core.admin import admin_site
from local_secrets.core.views import CustomTokenView

favicon_url = 'https://app.localsecrets.travel/media/template_media/Logo-LocalSecrets.png'

urlpatterns = (
    i18n_patterns(path(r'admin/', admin_site.urls))  # Admin pages
    + [
        # Favicon
        path(r'favicon.ico', RedirectView.as_view(url=favicon_url, permanent=True)),
        url(r'^auth/token/?$', CustomTokenView.as_view(), name='token'),
        # OAuth2 routes
        path(r'auth/', include('rest_framework_social_oauth2.urls')),
        # Local apps routes
        path(r'app_version/', include('local_secrets.app_version.urls')),
        path(r'2fa/', include('local_secrets.twofa.urls')),
        path(r'users/', include('local_secrets.users.urls')),
        path(r'sites/', include('local_secrets.sites.urls')),
        path(r'cities/', include('local_secrets.cities.urls')),
        path(r'policies/', include('local_secrets.core.urls')),
        path(r'travels/', include('local_secrets.travels.urls')),
        path(r'routes/', include('local_secrets.routes.urls')),
        path(r'translations/', include('local_secrets.languages.urls')),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.WELL_KNOWN_URL, document_root=settings.WELL_KNOWN_ROOT)
)
urlpatterns += staticfiles_urlpatterns()
