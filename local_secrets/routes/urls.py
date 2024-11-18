from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)

router.register('', views.RouteViewSet, basename='Routes')

urlpatterns = [
    path(r'', include(router.urls)),
]
