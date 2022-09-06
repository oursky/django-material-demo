from django.contrib.auth import get_user_model
from django.forms import EmailField, ModelForm, model_to_dict
from django.forms.widgets import RadioSelect
from material import Fieldset, Layout, Row
from material.frontend.views import (CreateModelView, DetailModelView,
                                     ModelViewSet, UpdateModelView)

from .library.django_superform import (ForeignKeyFormField, InlineFormSetField,
                                       SuperModelForm)
from .models import (Attachment, Choice, File, Question, QuestionFollower,
                     User, Vote)
from .utils import FormSetForm, get_html_list


class FileViewSet(ModelViewSet):
    model = File
    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AccountForm(ModelForm):
    email = EmailField(required=True)

    layout = Layout(
        'username',
        'email',
    )
    parent_instance_field = 'user'

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class UserForm(SuperModelForm):
    account = ForeignKeyFormField(AccountForm)

    layout = Layout(
        'account',
        'group',
        Row('subs_start', 'subs_expire'),
        'followed_users'
    )

    form_widgets = {'group': RadioSelect}

    class Meta:
        model = User
        fields = ['group', 'subs_start', 'subs_expire',
                  'followed_users']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.initial = model_to_dict(self.instance)

            account_queryset = self.instance.account
            self.initial["account"] = account_queryset


class UserDetailModelView(DetailModelView):
    def get_object_data(self):
        user = super().get_object()
        for item in super().get_object_data():
            yield item

        # M2M field
        followed_users = user.followed_users.order_by('account__username')
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


class UserUpdateModelView(UpdateModelView):
    def get_form_class(self):
        return UserForm

class UserViewSet(ModelViewSet):
    model = User
    detail_view_class = UserDetailModelView
    update_view_class = UserUpdateModelView

    list_display = ['account', 'group', 'followers_list']


class AttachmentsForm(FormSetForm):
    layout = Layout('file')
    parent_instance_field = 'question'

    class Meta:
        model = Attachment
        fields = ['file', 'question']


class QuestionFollowersForm(FormSetForm):
    layout = Layout(Row('follower', 'ordering'))
    parent_instance_field = 'question'

    class Meta:
        model = QuestionFollower
        fields = ['follower', 'ordering', 'question']


class ChoicesForm(FormSetForm):
    layout = Layout(Row('choice_text', 'vote_count'))
    parent_instance_field = 'question'

    class Meta:
        model = Choice
        fields = ['choice_text', 'vote_count', 'question']


class QuestionForm(SuperModelForm):
    # Formset fields
    attachments = InlineFormSetField(parent_model=Question,
                                     model=Attachment,
                                     form=AttachmentsForm, extra=0)

    q_followers = InlineFormSetField(parent_model=Question,
                                     model=QuestionFollower,
                                     form=QuestionFollowersForm, extra=0)

    choices = InlineFormSetField(parent_model=Question, model=Choice,
                                 form=ChoicesForm, extra=0)

    layout = Layout(
        'question_text',
        Row('total_vote_count', 'thumbnail'),
        Row('creator', 'show_creator'),
        'attachments',
        'q_followers',
        Fieldset('Date information',
                 'pub_date',
                 Row('vote_start', 'vote_end')),
        Fieldset('Vote restrictions',
                 'show_vote',
                 Row('has_max_vote_count', 'max_vote_count'),
                 Row('min_selection', 'max_selection'),
                 'allow_custom'),
        'choices')

    class Meta:
        model = Question
        fields = ['question_text', 'total_vote_count', 'thumbnail',
                  'creator', 'show_creator', 'pub_date',
                  'vote_start', 'vote_end', 'show_vote', 'has_max_vote_count',
                  'max_vote_count', 'min_selection', 'max_selection',
                  'allow_custom', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.formsets["attachments"].header = 'Attachments'
        self.formsets["q_followers"].header = 'Followers'
        self.formsets["choices"].header = 'Choices'

        if self.instance and self.instance.id:
            self.initial = model_to_dict(self.instance)

            attachments_queryset = self.instance.attachment_set.all()
            self.initial["attachments"] = attachments_queryset
            self.formsets["attachments"].queryset = attachments_queryset

            followers_queryset = (
                self.instance.questionfollower_set.order_by('-ordering'))
            self.initial["q_followers"] = followers_queryset
            self.formsets["q_followers"].queryset = followers_queryset

            choices_queryset = self.instance.choice_set.all()
            self.initial["choices"] = choices_queryset
            self.formsets["choices"].queryset = choices_queryset


class QuestionCreateView(CreateModelView):
    def get_form_class(self):
        return QuestionForm


class QuestionUpdateView(UpdateModelView):
    def get_form_class(self):
        return QuestionForm


class QuestionViewSet(ModelViewSet):
    model = Question
    create_view_class = QuestionCreateView
    update_view_class = QuestionUpdateView

    list_display = ['question_text', 'creator', 'vote_start',
                    'vote_end', 'selection_bounds']


class VoteViewSet(ModelViewSet):
    model = Vote
    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
