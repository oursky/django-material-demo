from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db.models import Count
from django.forms import (BaseInlineFormSet, BooleanField, EmailField,
                          ModelForm, model_to_dict)
from django.forms.widgets import CheckboxInput, RadioSelect
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic.edit import FormView
from django_filters import CharFilter, NumberFilter
from material import Fieldset, Layout, Row
from material.frontend.views import (CreateModelView, DetailModelView,
                                     ListModelView, ModelViewSet,
                                     UpdateModelView)

from .library.django_superform import (ForeignKeyFormField, InlineFormSetField,
                                       SuperModelForm)
from .models import (Attachment, Choice, File, Question, QuestionFollower,
                     Settings, User, Vote)
from .utils import (FieldDataMixin, FormSetForm, GetParamAsFormDataMixin,
                    ListFilterView, NestedModelFormField, SearchAndFilterSet,
                    get_html_list)


class FileViewSet(ModelViewSet):
    model = File
    list_display = ['file_name', 'file_type', 'file_size', 'storage_loc']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AccountForm(UserChangeForm):
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


class UserUpdateView(UpdateModelView):
    def get_form_class(self):
        return UserForm


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
    detail_view_class = UserDetailView
    update_view_class = UserUpdateView
    list_view_class = UserListView


class AttachmentsForm(FormSetForm):
    layout = Layout('file')
    parent_instance_field = 'question'

    class Meta:
        model = Attachment
        fields = ['file']


class QuestionFollowersForm(FormSetForm):
    layout = Layout(Row('follower', 'ordering'))
    parent_instance_field = 'question'

    class Meta:
        model = QuestionFollower
        fields = ['follower', 'ordering']


class QuestionFollowersFormSet(BaseInlineFormSet):
    # Formset validation
    def clean(self):
        super().clean()

        followers = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            follower = form.cleaned_data.get('follower')
            if follower in followers:
                self.add_error(NON_FIELD_ERRORS, ValidationError(
                    'Please correct the duplicate values below.',
                    'unique'))
                break
            followers.append(follower)


class ChoicesForm(FormSetForm):
    layout = Layout(Row('choice_text', 'vote_count'))
    parent_instance_field = 'question'

    class Meta:
        model = Choice
        fields = ['choice_text', 'vote_count']


class MaxVoteCountForm(ModelForm, FieldDataMixin):
    # If want to add attrs declaratively
    # has_max_vote_count = BooleanField(
    #     required=False,
    #     widget=CheckboxInput(attrs={'data-reload-form': True}))

    layout = Layout(Row('has_max_vote_count', 'max_vote_count'))
    template_name = 'polls/forms/max_vote_count_form.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        has_max_vote_count = self.fields['has_max_vote_count']
        max_vote_count = self.fields['max_vote_count']
        toggle = self.get_field_value('has_max_vote_count')

        # reload form when field value is changed (add attrs imperatively)
        has_max_vote_count.widget.attrs.update({'data-reload-form': True})
        # make max_vote_count editable depending on has_max_vote_count value
        if toggle:
            max_vote_count.widget.attrs.update(required=True)
        else:
            max_vote_count.widget.attrs.update(disabled=True, value='')

    class Meta:
        model = Question
        fields = ['has_max_vote_count', 'max_vote_count']

    class Media:
        js = ['js/reload_form.js']


class QuestionForm(SuperModelForm):
    max_vote_count_control = NestedModelFormField(MaxVoteCountForm)

    # Formset fields
    attachments = InlineFormSetField(parent_model=Question,
                                     model=Attachment,
                                     form=AttachmentsForm, extra=0)

    q_followers = InlineFormSetField(parent_model=Question,
                                     model=QuestionFollower,
                                     form=QuestionFollowersForm,
                                     formset=QuestionFollowersFormSet, extra=0)

    choices = InlineFormSetField(parent_model=Question, model=Choice,
                                 form=ChoicesForm, extra=0,
                                 validate_min=True, min_num=2)

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
                 'max_vote_count_control',
                 Row('min_selection', 'max_selection'),
                 'allow_custom'),
        'choices')

    class Meta:
        model = Question
        fields = ['question_text', 'total_vote_count', 'thumbnail',
                  'creator', 'show_creator', 'pub_date',
                  'vote_start', 'vote_end', 'show_vote', 'has_max_vote_count',
                  'max_vote_count', 'min_selection', 'max_selection',
                  'allow_custom']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.formsets["attachments"].header = 'Attachments'
        self.formsets["q_followers"].header = 'Followers'
        self.formsets["choices"].header = 'Choices'

        if self.instance and self.instance.id:
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

    # Related field validations
    def check_vote_end(self):
        vote_end = self.cleaned_data['vote_end']
        vote_start = self.cleaned_data['vote_start']

        if (vote_start is not None
                and vote_end is not None
                and vote_start > vote_end):
            self.add_error('vote_end', ValidationError(
                'Ensure this time is later than the vote start date.',
                'vote_end_too_early'))

    def check_max_vote_count(self):
        max_vote_count = self.cleaned_data['max_vote_count']
        has_max_vote_count = self.cleaned_data['has_max_vote_count']

        if max_vote_count is None and has_max_vote_count:
            self.add_error('max_vote_count',
                           ValidationError('This field is required.',
                                           'max_vote_count_required'))

        if max_vote_count is not None and max_vote_count < 0:
            self.add_error('max_vote_count',
                           ValidationError('Ensure this value is positive.',
                                           'max_vote_count_positive'))

    def check_selection_bounds(self):
        min_selection = self.cleaned_data['min_selection']
        max_selection = self.cleaned_data['max_selection']
        choices = self.formsets['choices']

        if (min_selection is not None
                and max_selection is not None
                and min_selection > max_selection):
            self.add_error('max_selection', ValidationError(
                'Ensure this value is greater than or equal to '
                'the min selection.',
                'max_selection_too_small'))

        if (min_selection is not None
                and min_selection > len(choices)):
            self.add_error('min_selection', ValidationError(
                'Ensure this value is less than or equal to '
                'the number of choices (%(len)s).',
                'max_selection_too_small',
                params={'len': len(choices)}))

    def check_total_vote_count(self):
        total_vote_count = self.cleaned_data['total_vote_count']

        has_max_vote_count = self.cleaned_data.get('has_max_vote_count', None)
        if not has_max_vote_count:
            return total_vote_count

        max_vote_count = self.cleaned_data['max_vote_count']

        if max_vote_count and total_vote_count > max_vote_count:
            self.add_error('max_vote_count', ValidationError(
                'Ensure total vote count is less than or equal to '
                'the max vote count.',
                'total_vote_count_too_big'))

    def clean(self):
        super().clean()

        self.check_vote_end()
        self.check_max_vote_count()
        self.check_selection_bounds()
        self.check_total_vote_count()

        # Full form 'validation'
        error_count = len(self.errors)
        for _, formset in self.formsets.items():
            error_count += formset.total_error_count()
        if error_count > 0:
            self.add_error(NON_FIELD_ERRORS, ValidationError(
                'Please correct the error(s) below (%(len)s total).',
                params={'len': error_count}
            ))


class QuestionCreateView(CreateModelView, GetParamAsFormDataMixin):
    def get_form_class(self):
        return QuestionForm


class QuestionUpdateView(UpdateModelView, GetParamAsFormDataMixin):
    def get_form_class(self):
        return QuestionForm


class QuestionFilterForm(forms.Form):
    layout = Layout('search',
                    'question_text',
                    'show_vote')


class QuestionFilter(SearchAndFilterSet):
    search_fields = ['question_text', 'creator__account__username',
                     'choice__choice_text']

    question_text = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Question
        fields = {'show_vote': ['exact']}
        form = QuestionFilterForm


class QuestionListView(ListModelView, ListFilterView):
    list_display = ['question_text', 'creator', 'choice_list',
                    'vote_start', 'vote_end', 'selection_bounds']
    filterset_class = QuestionFilter


class QuestionViewSet(ModelViewSet):
    model = Question
    create_view_class = QuestionCreateView
    update_view_class = QuestionUpdateView
    list_view_class = QuestionListView


class VoteViewSet(ModelViewSet):
    model = Vote
    list_display = ['timestamp', 'question', 'choice_text', 'is_custom']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class PasswordChangeView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Form for changing password')


class PasswordChangeDoneView(generic.View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Password changed!')


class SettingsForm(forms.Form):
    primary_color = forms.CharField(label='Primary color', required=False)
    primary_color_light = forms.CharField(
        label='Primary color light', required=False)
    primary_color_dark = forms.CharField(
        label='Primary color dark', required=False)
    secondary_color = forms.CharField(label='Secondary color', required=False)
    secondary_color_light = forms.CharField(
        label='Secondary color light', required=False)
    success_color = forms.CharField(label='Success color', required=False)
    error_color = forms.CharField(label='Error color', required=False)
    link_color = forms.CharField(label='Link color', required=False)


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class SettingsView(FormView):
    form_class = SettingsForm
    template_name = 'polls/settings.html'

    def get_initial(self):
        return model_to_dict(Settings(session=self.request.session))

    def form_valid(self, form):
        settings = Settings(session=self.request.session)
        for k, v in form.cleaned_data.items():
            setattr(settings, k, v)

        settings.save()
        return redirect('polls:settings')
