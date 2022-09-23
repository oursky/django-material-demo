from django.urls import reverse
from material.frontend.apps import ModuleMixin
from material.frontend.urlconf import ModuleURLResolver

class ModuleNamespaceMixin(ModuleMixin):
    base_url = None
    namespace = None

    @property
    def urls(self):
        return ModuleURLResolver(self.base_url, self.get_urls(), module=self, app_name=self.namespace, namespace=self.namespace)

    def index_url(self):
        return reverse('{}:index'.format(self.namespace))
