from django.apps import AppConfig
from material.frontend.apps import ModuleMixin
from material.frontend.urlconf import ModuleURLResolver


class CmsPollsConfig(ModuleMixin, AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms.polls'
    label = 'polls'
    verbose_name = 'CMS Polls'
    base_url = 'cms/polls/'

    @property
    def urls(self):
        return ModuleURLResolver(self.base_url, self.get_urls(), module=self, app_name=self.label, namespace=self.label)
