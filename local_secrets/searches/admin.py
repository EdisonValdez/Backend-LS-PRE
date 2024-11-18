from local_secrets.sites.admin import CategoryAdmin, LevelAdmin, SubCategoryAdmin
from .models import CategoryForAdmin, LevelForAdmin, SubcategoryForAdmin
from ..core.admin import admin_site

admin_site.register(LevelForAdmin, LevelAdmin)
admin_site.register(CategoryForAdmin, CategoryAdmin)
admin_site.register(SubcategoryForAdmin, SubCategoryAdmin)
