from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import EmailField, IntegerField
from django.forms.widgets import RadioSelect
from django.http import HttpResponse
from django.views import generic
from django_filters import CharFilter, NumberFilter
from library.django_superform import (ForeignKeyFormField, InlineFormSetField,
                                      ModelFormField, SuperModelForm)
from material import Layout, Row
from material.frontend.views import (CreateModelView, DetailModelView,
                                     ListModelView, ModelViewSet,
                                     UpdateModelView)
from polls.models import QuestionFollower, User, UserFollower

from ...utils import (FormSetForm, ListFilterView, SearchAndFilterSet,
                      get_html_list)


class AccountCreateForm(UserCreationForm):
    email = EmailField(required=True)

    layout = Layout(
        'username',
        'email',
        Row('password1', 'password2'),
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class UserCreateForm(SuperModelForm):
    account = ModelFormField(AccountCreateForm)

    layout = Layout(
        'account',
        'group',
        Row('subs_start', 'subs_expire')
    )

    class Meta:
        model = User
        fields = ['group', 'subs_start', 'subs_expire']
        widgets = {'group': RadioSelect}

    def save(self, commit=True):
        if commit:
            # manually save account form before main form
            form = self.forms['account']
            field = self.composite_fields['account']
            account_instance = field.save(self, 'account', form, commit=commit)
            if account_instance:
                self.instance.account = account_instance

            return self.save_form(commit=commit)
        else:
            return super().save(commit)


class AccountUpdateForm(UserChangeForm):
    email = EmailField(required=True)

    layout = Layout(
        'username',
        'email',
        'password',
        Row('first_name', 'last_name'),
        'groups',
        'user_permissions',
        'is_active',
        Row('is_staff', 'is_superuser'),
        Row('date_joined', 'last_login'),
    )


class FollowedUsersForm(FormSetForm):
    layout = Layout(Row('followed_user', 'ordering'),
                    Row('enable_email_notify', 'notify_time'))
    parent_instance_field = 'follower'

    class Meta:
        model = UserFollower
        fields = ['followed_user', 'ordering',
                  'enable_email_notify', 'notify_time']

    def clean_notify_time(self):
        time = self.cleaned_data['notify_time']
        if time:
            time = time.replace(second=0, microsecond=0)
        return time


class FollowedQuestionsForm(FormSetForm):
    layout = Layout(Row('question', 'ordering'),
                    Row('enable_email_notify', 'notify_time'))
    parent_instance_field = 'follower'

    class Meta:
        model = QuestionFollower
        fields = ['question', 'ordering', 'enable_email_notify', 'notify_time']

    def clean_notify_time(self):
        time = self.cleaned_data['notify_time']
        if time:
            time = time.replace(second=0, microsecond=0)
        return time


class UserUpdateForm(SuperModelForm):
    account = ForeignKeyFormField(AccountUpdateForm)
    subs_day_count = IntegerField(min_value=0, required=False,
                                  label='Subscription duration (in days)')

    followed_users = InlineFormSetField(parent_model=User,
                                        model=UserFollower,
                                        form=FollowedUsersForm,
                                        fk_name='follower', extra=0)
    followed_questions = InlineFormSetField(parent_model=User,
                                            model=QuestionFollower,
                                            form=FollowedQuestionsForm, extra=0)

    layout = Layout(
        'account',
        'group',
        Row('subs_start', 'subs_day_count'),
        'followed_users',
        'followed_questions',
    )

    class Meta:
        model = User
        fields = ['group', 'subs_start']
        widgets = {'group': RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.formsets["followed_users"].header = 'Followed Users'
        self.formsets["followed_questions"].header = 'Followed Questions'

        if self.instance and self.instance.pk:
            account_qs = self.instance.account
            self.initial["account"] = account_qs

            if self.instance.subs_start and self.instance.subs_expire:
                date_delta = (self.instance.subs_expire
                              - self.instance.subs_start)
                self.initial["subs_day_count"] = date_delta.days

            followed_users_qs = (
                self.instance.user_follows.order_by('-ordering'))
            self.initial["followed_users"] = followed_users_qs
            self.formsets["followed_users"].queryset = followed_users_qs

            followed_questions_qs = (
                self.instance.questionfollower_set.order_by('-ordering'))
            self.initial["followed_questions"] = followed_questions_qs
            self.formsets["followed_questions"].queryset = followed_questions_qs

    def clean(self):
        super().clean()
        subs_start = self.cleaned_data.get('subs_start', None)
        subs_day_count = self.cleaned_data.get('subs_day_count', None)
        if subs_start is None and subs_day_count is not None:
            self.add_error('subs_start', ValidationError(
                'This field is required if subscription duration is provided.',
                'required'))

    def save(self, commit=True):
        instance = super().save(commit)
        subs_start = instance.subs_start
        subs_day_count = self.cleaned_data.get('subs_day_count', None)
        if subs_start and subs_day_count is not None:
            subs_expire = subs_start + timedelta(days=subs_day_count)
            instance.subs_expire = subs_expire
            instance.save()
        return instance


class UserCreateView(CreateModelView):
    def get_form_class(self):
        return UserCreateForm


class UserUpdateView(UpdateModelView):
    def get_form_class(self):
        return UserUpdateForm


class UserDetailView(DetailModelView):
    def get_object_data(self):
        user = super().get_object()

        # Account fields
        account = user.account

        account_fields = [
            'username', 'email',  # 'password',
            'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login',
        ]
        for field in account_fields:
            attr = getattr(account, field, '')
            if attr:
                yield (field.replace('_', ' ').title(), attr)

        auth_groups = account.groups.all()
        html_list = get_html_list(auth_groups)
        yield ('Auth Groups', html_list or None)

        user_permissions = account.user_permissions.all()
        html_list = get_html_list(user_permissions)
        yield ('User Permissions', html_list or None)

        # Polls fields
        account_name = User._meta.get_field('account')
        account_name = account_name.verbose_name.title()
        group_name = User._meta.get_field('group')
        group_name = group_name.verbose_name.title()
        for item in super().get_object_data():
            if item[0] == account_name:
                continue
            elif item[0] == group_name:
                yield ('Polls Group', item[1])
            else:
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


class UserFilterForm(forms.Form):
    layout = Layout('search',
                    'group',
                    'account__username',
                    'min_follower_count')


class UserFilter(SearchAndFilterSet):
    search_fields = ['account__username', 'group']

    account__username = CharFilter(lookup_expr='icontains',
                                   label='Name contains')

    min_follower_count = NumberFilter(field_name='user_followed',
                                      method='filter_count_gte',
                                      label='Minimum follower count')

    def filter_count_gte(self, queryset, name, value):
        qs = queryset.annotate(name_count=Count(name))
        return qs.filter(name_count__gte=value)

    class Meta:
        model = User
        fields = {'group': ['exact']}
        form = UserFilterForm


class UserListView(ListModelView, ListFilterView):
    list_display = ['name', 'group', 'followers_list']
    filterset_class = UserFilter


class UserViewSet(ModelViewSet):
    model = User
    create_view_class = UserCreateView
    update_view_class = UserUpdateView
    detail_view_class = UserDetailView
    list_view_class = UserListView


class PasswordChangeView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Form for changing password')


class PasswordChangeDoneView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Password changed!')
