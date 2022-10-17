from django.apps import AppConfig
from material.frontend.apps import ModuleMixin


class CmsOthersConfig(ModuleMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    icon = '<i class="material-icons">dashboard_customize</i>'
    name = 'cms.others'
    label = 'others'
