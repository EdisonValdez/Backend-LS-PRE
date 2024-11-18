from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from . import views
from .models import Category

router = routers.DefaultRouter(trailing_slash=False)

router.register('categories', views.CategoryViewSet, basename='Categories')
#router.register('category-autocomplete', views.CategoryAutocomplete.as_view(model=Category), basename='CategoryAutocomplete')
router.register('comments', views.CommentViewSet, basename='Comments')
router.register('default_images', views.DefaultImageViewSet, basename='DefaultImages')
router.register('', views.SiteViewSet, basename='Sites')

urlpatterns = [
    path(r'', include(router.urls)),
    re_path('^category-autocomplete/$', views.CategoryAutocomplete.as_view(), name='category-autocomplete'),
    re_path('^level-autocomplete/$', views.LevelAutocomplete.as_view(), name='level-autocomplete'),
    re_path('^place-level-autocomplete/$', views.PlaceLevelAutocomplete.as_view(), name='place-level-autocomplete'),
    re_path('^event-level-autocomplete/$', views.EventLevelAutocomplete.as_view(), name='event-level-autocomplete'),
    re_path('^subcategory-autocomplete/$', views.SubCategoryAutocomplete.as_view(), name='subcategory-autocomplete'),
]
