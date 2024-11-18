from django.utils.translation import gettext_lazy as _

from local_secrets.sites.models import Category, Level, SubCategory


class LevelForAdmin(Level):
    class Meta:
        proxy = True

        verbose_name = _('Search level')
        verbose_name_plural = _('Search levels')


class CategoryForAdmin(Category):
    class Meta:
        proxy = True

        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class SubcategoryForAdmin(SubCategory):
    class Meta:
        proxy = True

        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')
