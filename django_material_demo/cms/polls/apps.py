from django.apps import AppConfig

from ..utils import ModuleNamespaceMixin


class CmsPollsConfig(ModuleNamespaceMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms.polls'
    label = 'cms_polls'
    verbose_name = 'Polls'

    base_url = 'polls/'
    # this should match the app_name of the models
    namespace = 'polls'
