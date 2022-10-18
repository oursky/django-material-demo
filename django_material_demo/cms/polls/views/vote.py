from material.frontend.views import ListModelView, ModelViewSet
from polls.models import Vote

from ...utils import ListFilterView
from ...utils.views import DeletedListMixin


class VoteListView(ListModelView):
    template_name = 'material/frontend/views/filter_list.html'

class VoteViewSet(ModelViewSet, DeletedListMixin):
    model = Vote
    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']
    list_view_class = VoteListView

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
