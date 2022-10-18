from django import forms
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db.models import F
from django.forms import (BaseInlineFormSet, BooleanField, FileField,
                          ImageField, ModelForm)
from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple
from django.template.loader import render_to_string
from django.utils import timezone
from django_filters import DateTimeFilter, TypedMultipleChoiceFilter
from django_superform import InlineFormSetField, SuperModelForm
from material import Fieldset, Layout, Row
from material.frontend.views import (CreateModelView, DetailModelView,
                                     ListModelView, ModelViewSet,
                                     UpdateModelView)
from modeltranslation.utils import get_translation_fields
from polls.models import Attachment, Choice, Question, QuestionFollower, User

from ...utils.forms import (FieldDataMixin, GetParamAsFormDataMixin,
                            NestedModelFormField)
from ...utils.views import (ActionChoices, ActionHandler, DeletedListMixin,
                            DeletedListModelView, ListActionMixin,
                            ListFilterView, SearchAndFilterSet)


class AttachmentsForm(ModelForm):
    file = FileField(label="Attachment",
                     max_length=settings.FILE_UPLOAD_MAX_MEMORY_SIZE)

    layout = Layout('file')
    parent_instance_field = 'question'

    class Meta:
        model = Attachment
        fields = ['file']


class QuestionFollowersForm(ModelForm):
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


class ChoicesForm(ModelForm):
    layout = Layout(Row(*get_translation_fields('choice_text'), 'vote_count'))
    parent_instance_field = 'question'

    class Meta:
        model = Choice
        fields = [*get_translation_fields('choice_text'), 'vote_count']


class MaxVoteCountForm(ModelForm, FieldDataMixin):
    # If want to add attrs declaratively
    # has_max_vote_count = BooleanField(
    #     required=False,
    #     widget=CheckboxInput(attrs={'data-reload-form': True}))

    layout = Layout(Row('has_max_vote_count', 'max_vote_count'))

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


class QuestionForm(SuperModelForm, FieldDataMixin):
    thumbnail = ImageField(required=False, label='Thumbnail',
                           max_length=settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
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
        *get_translation_fields('question_text'),
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
        fields = [*get_translation_fields('question_text'),
                  'total_vote_count', 'thumbnail',
                  'creator', 'show_creator', 'pub_date',
                  'vote_start', 'vote_end', 'show_vote', 'has_max_vote_count',
                  'max_vote_count', 'min_selection', 'max_selection',
                  'allow_custom']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_initial_data()
        self.adjust_field_attrs()

    def set_initial_data(self):
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

    def should_disable_question_text(self):
        try:
            vote_start = self.get_field_value('vote_start').timestamp()
            vote_end = self.get_field_value('vote_end').timestamp()
            now = timezone.now().timestamp()
            return vote_start <= now <= vote_end
        except AttributeError:
            return False  # vote_start/vote_end field value is None

    def adjust_field_attrs(self):
        # Prevent changing question when poll in progress
        if self.should_disable_question_text():
            for field_name in get_translation_fields('question_text'):
                self.fields[field_name].disabled = True

    # Related field validations
    def check_vote_end(self):
        vote_end = self.cleaned_data.get('vote_end', None)
        vote_start = self.cleaned_data.get('vote_start', None)

        if (vote_start is not None
                and vote_end is not None
                and vote_start > vote_end):
            self.add_error('vote_end', ValidationError(
                'Ensure this time is later than the vote start date.',
                'vote_end_too_early'))

    def check_max_vote_count(self):
        max_vote_count = self.cleaned_data.get('max_vote_count', None)
        has_max_vote_count = self.cleaned_data.get('has_max_vote_count', None)

        if max_vote_count is None and has_max_vote_count:
            self.add_error('max_vote_count',
                           ValidationError('This field is required.',
                                           'max_vote_count_required'))

        if max_vote_count is not None and max_vote_count < 0:
            self.add_error('max_vote_count',
                           ValidationError('Ensure this value is positive.',
                                           'max_vote_count_positive'))

    def check_selection_bounds(self):
        min_selection = self.cleaned_data.get('min_selection', None)
        max_selection = self.cleaned_data.get('max_selection', None)
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
        total_vote_count = self.cleaned_data.get('total_vote_count', None)

        has_max_vote_count = self.cleaned_data.get('has_max_vote_count', None)
        if not has_max_vote_count:
            return total_vote_count

        max_vote_count = self.cleaned_data.get('max_vote_count', None)

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
    template_name = 'material/frontend/views/media_form.html'

    def get_initial(self):
        initial = super().get_initial()
        # Set initial creator to current user
        user = User.objects.filter(account=self.request.user)
        if len(user) == 1:
            initial['creator'] = user[0]
        return initial

    def get_form_class(self):
        return QuestionForm


class QuestionUpdateView(UpdateModelView, GetParamAsFormDataMixin):
    template_name = 'material/frontend/views/media_form.html'

    def get_form_class(self):
        return QuestionForm


class QuestionFilterForm(forms.Form):
    layout = Layout('search',
                    'show_vote',
                    'creator__isnull',
                    'pub_date__gt', 'pub_date__lt')


def str_to_bool(s):
    return str(s).lower() in ['true', 'yes', '1']


class QuestionFilter(SearchAndFilterSet):
    search_fields = ['question_text', 'creator__account__username',
                     'choice__choice_text']

    pub_date__gt = DateTimeFilter(field_name='pub_date', lookup_expr='gt',
                                  label='Published after')
    pub_date__lt = DateTimeFilter(field_name='pub_date', lookup_expr='lt',
                                  label='Published before')

    NEGATED_BOOLEAN_CHOICES = ((False, 'Yes'), (True, 'No'))
    creator__isnull = TypedMultipleChoiceFilter(
        choices=NEGATED_BOOLEAN_CHOICES, label='Has creator',
        coerce=str_to_bool, widget=CheckboxSelectMultiple)

    class Meta:
        model = Question
        fields = {'show_vote': ['exact'], 'creator': ['isnull']}
        form = QuestionFilterForm


class QuestionActionChoices(ActionChoices):
    RESET_VOTE = 'reset_vote'
    ADD_VOTE = ('add_vote', 'Add One Vote')


class QuestionActionHandler(ActionHandler):
    def reset_vote(self, model, pk_list):
        model.objects.filter(pk__in=pk_list).update(total_vote_count=0)

    def add_vote(self, model, pk_list):
        model.objects.filter(pk__in=pk_list).update(
            total_vote_count=F('total_vote_count')+1)


class QuestionListView(ListActionMixin, ListModelView, ListFilterView):
    list_display = [
        'question_text', 'creator', 'choice_list', 'show_vote',
        'pub_date', 'total_vote_count'
    ]
    filterset_class = QuestionFilter
    action_choices = QuestionActionChoices
    action_handler = QuestionActionHandler


class QuestionDeletedListView(DeletedListModelView):
    list_display = ['question_text', 'creator', 'choice_list']


class QuestionDetailView(DetailModelView):
    def get_object_data(self):
        question = super().get_object()
        thumbnail_name = Question._meta.get_field('thumbnail')
        thumbnail_name = thumbnail_name.verbose_name.title()
        for item in super().get_object_data():
            if item[0] == thumbnail_name:
                if item[1]:
                    ctx = {'attrs': {
                        'class': 'thumbnail',
                        'src': item[1].url,
                        'alt': item[1].name
                    }}
                    image_html = render_to_string('data/img.html', ctx)
                    yield (item[0], image_html)
                else:
                    yield (item[0], 'None')
            else:
                yield item

        attachments = question.attachment_set.all()
        attachment_links = []
        for attachment in attachments:
            ctx = {
                'content': attachment.file.name,
                'attrs': {
                    'href': attachment.file.url,
                    'download': True
                },
            }
            attachment_links.append(render_to_string('data/a.html', ctx))
        ctx = {'items': attachment_links}
        html_list = render_to_string('data/ul.html', ctx)
        yield ('Attachments', html_list)


class QuestionViewSet(ModelViewSet, DeletedListMixin):
    model = Question
    create_view_class = QuestionCreateView
    update_view_class = QuestionUpdateView
    list_view_class = QuestionListView
    deleted_list_view_class = QuestionDeletedListView
    detail_view_class = QuestionDetailView
