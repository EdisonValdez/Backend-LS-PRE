from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)

router.register('', views.TwoFAViewset, basename='2FA')

urlpatterns = [
    path(r'', include(router.urls)),
]
