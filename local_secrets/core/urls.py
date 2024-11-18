from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)

router.register('', views.PoliciesViewSet, basename='Policies')
router.register('info', views.InfoViewSet, basename='Info')

urlpatterns = [
    path(r'', include(router.urls)),
]
