from django.views.generic import ListView
from polls.models import Choice, Question, User, Vote


class DeletedObjectListView(ListView):
    soft_delete_models = [Choice, Question, User, Vote]
    template_name = 'cms_polls/deleted_objects.html'

    def get_queryset(self):
        soft_deleted_objs = []
        for model in self.soft_delete_models:
            soft_deleted_objs.extend(model.deleted_objects.all())
        return sorted(soft_deleted_objs, key=lambda x: x.deleted, reverse=True)

    def get_context_data(self, **kwargs):
        kwargs['headers'] = ['Object', 'Model', 'Deleted at']
        kwargs['data'] = [(x, x._meta.model_name.title(), x.deleted)
                          for x in self.get_queryset()]
        return super().get_context_data(**kwargs)
