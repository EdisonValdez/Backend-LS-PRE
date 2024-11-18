from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)

router.register('countries', views.CountryViewSet, basename='Countries')
router.register('', views.CityViewSet, basename='Cities')

urlpatterns = [
    path(r'', include(router.urls)),
    re_path('^city-autocomplete/$', views.CityAutocomplete.as_view(), name='city-autocomplete'),
]
