from django.forms.widgets import EmailInput, RadioSelect
from material import Fieldset, Layout, Row
from material.frontend.views import ModelViewSet

from .models import File, Question, User, Vote


class FileViewSet(ModelViewSet):
    model = File
    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class UserViewSet(ModelViewSet):
    model = User
    layout = Layout(
        'name',
        'email',
        'group',
        Row('subs_start', 'subs_expire'),
        'followers'
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
    list_display = ['question_text', 'pub_date', 'vote_start',
                    'vote_end', 'followers', 'selection_bounds']


class VoteViewSet(ModelViewSet):
    model = Vote
    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
