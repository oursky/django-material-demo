from django.forms.widgets import EmailInput, RadioSelect
from material import Fieldset, Layout, Row
from material.frontend.views import DetailModelView, ModelViewSet

from .models import File, Question, User, Vote
from .utils import get_html_list


class FileViewSet(ModelViewSet):
    model = File
    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class UserDetailModelView(DetailModelView):
    def get_object_data(self):
        user = super().get_object()
        for item in super().get_object_data():
            yield item

        # M2M field
        followed_users = user.followed_users.order_by('name')
        if len(followed_users):
            html_list = get_html_list(followed_users)
            yield ('Followed Users', html_list)

        # Reverse relation
        followed_question = user.question_follows.order_by('question_text')
        html_list = get_html_list(followed_question)
        yield ('Followed Question', html_list or 'None')

        # Relational data
        question_rel = user.questionfollower_set
        notify_time = question_rel.filter(notify_time__isnull=False)
        notify_time = notify_time.values_list('notify_time', flat=True)
        html_list = get_html_list(notify_time)
        yield ('Question Notify Times', html_list or 'None')


class UserViewSet(ModelViewSet):
    model = User
    detail_view_class = UserDetailModelView
    layout = Layout(
        'name',
        'email',
        'group',
        Row('subs_start', 'subs_expire'),
        'followed_users'
    )

    form_widgets = {'email': EmailInput,
                    'group': RadioSelect}
    list_display = ['name', 'group', 'followers_list']


class QuestionViewSet(ModelViewSet):
    model = Question
    layout = Layout(
        'question_text',
        Row('total_vote_count', 'thumbnail'),
        Row('creator', 'show_creator'),
        'followers',
        Fieldset('Date information',
                 'pub_date',
                 Row('vote_start', 'vote_end')),
        Fieldset('Vote restrictions',
                 'show_vote',
                 Row('has_max_vote_count', 'max_vote_count'),
                 Row('min_selection', 'max_selection'),
                 'allow_custom'))
    form_widgets = {}
    list_display = ['question_text', 'creator', 'vote_start',
                    'vote_end', 'selection_bounds']


class VoteViewSet(ModelViewSet):
    model = Vote
    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
