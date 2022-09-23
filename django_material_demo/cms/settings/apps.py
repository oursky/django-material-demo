from django.apps import AppConfig
from material.frontend.apps import ModuleMixin


class CmsSettingsConfig(ModuleMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    icon = '<i class="material-icons">settings</i>'
    name = 'cms.settings'
    label = 'settings'
