from functools import reduce
from operator import or_

from django.db.models import Q
from django.forms import ModelForm
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import (ModelFormMixin, ProcessFormView,
                                       UpdateView)
from django_filters import CharFilter, FilterSet
from django_filters.views import FilterView

from library.django_superform import ModelFormField


def get_html_list(arr):
    """Generate a HTML unordered list from an iterable

    Return an empty string instead when iterable is empty
    """
    if len(arr) == 0:
        return ''

    value_list = [conditional_escape(x) for x in arr]
    value_list_html = mark_safe(
        '<ul>'
        + ''.join('<li>' + x + '</li>' for x in value_list)
        + '</ul>')
    return value_list_html


class FormSetForm(ModelForm):
    parent_instance_field = ''

    def __init__(self, parent_instance=None,
                 get_formset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_instance = parent_instance
        self.formset = get_formset and get_formset()

    def save(self, commit):
        setattr(self.instance, self.parent_instance_field, self.parent_instance)
        return super().save(commit)

    def full_clean(self):
        super().full_clean()
        # NOTE: Ignore parent instance foreign key error as we save ourselves
        if self._errors.get(self.parent_instance_field):
            self._errors.pop(self.parent_instance_field)


class NestedModelFormField(ModelFormField):
    def get_instance(self, form, name):
        if form._meta.model != self.form_class._meta.model:
            raise ValueError('Field model must be same as the form model')
        return form.instance


class GetParamAsFormDataMixin(SingleObjectTemplateResponseMixin,
                              ModelFormMixin, ProcessFormView):
    # mixin to be used with CreateView or UpdateView
    def get(self, request, *args, **kwargs):
        if request.GET:
            # form data included in GET request, use it to initialize form
            form_class = self.get_form_class()
            form = form_class(request.GET)

            if isinstance(self, UpdateView):
                self.object = self.get_object()
            else:
                # self is CreateView, no associated object
                self.object = None
            return self.render_to_response(self.get_context_data(form=form))
        # no form data, fallback to default
        return super().get(request, *args, **kwargs)


class FieldDataMixin(object):
    def get_field_value(self, field_name):
        if self.is_bound:
            # get value from boundfield
            return self[field_name].value()
        else:
            # use initial value
            return self.initial.get(field_name)


class ListFilterView(FilterView):
    template_name = 'material/frontend/views/filter_list.html'

    def get_object_list(self):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        if (not self.filterset.is_bound
                or self.filterset.is_valid()
                or not self.get_strict()):
            return self.filterset.qs
        else:
            return self.filterset.queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        context.update({'filter': self.filterset})
        return context


class SearchAndFilterSet(FilterSet):
    # fields to search values from
    search_fields = []
    search = CharFilter(method='keyword_search', label='Search')

    def keyword_search(self, queryset, name, value):
        # search if any keyword is in any provided search fields
        # assume value is a space separated list of keywords
        queries = [Q(**{field + '__icontains': keyword})
                   for field in self.search_fields
                   for keyword in value.strip().split()]

        return queryset.filter(reduce(or_, queries, Q())).distinct()
