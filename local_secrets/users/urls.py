from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)

router.register('create', views.UserCreationViewSet, basename='CreateUser')
router.register('', views.UserViewSet, basename='Users')
router.register('tags', views.TagViewSet, basename='Tags')

urlpatterns = [
    path(r'', include(router.urls)),
]
