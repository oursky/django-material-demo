from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.forms import BaseInlineFormSet, BooleanField, ModelForm
from django.forms.widgets import CheckboxInput
from django_filters import CharFilter
from library.django_superform import InlineFormSetField, SuperModelForm
from material import Fieldset, Layout, Row
from material.frontend.views import (CreateModelView, ListModelView,
                                     ModelViewSet, UpdateModelView)
from polls.models import Attachment, Choice, Question, QuestionFollower
from components.widgets.switch import Switch

from ...utils import (FieldDataMixin, FormSetForm, GetParamAsFormDataMixin,
                      ListFilterView, NestedModelFormField, SearchAndFilterSet)


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
    template_name = 'cms_polls/forms/max_vote_count_form.html'

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
        widgets = {
            'show_creator': Switch,
        }

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
