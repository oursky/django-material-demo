from functools import reduce
from operator import or_

from django import forms
from django.db.models import Q, TextChoices
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django_filters import CharFilter, FilterSet
from django_filters.views import FilterView
from material.frontend.views import ListModelView
from safedelete.config import DELETED_ONLY_VISIBLE


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

    def total(self):
        if hasattr(super(), 'get_object_list'):
            return super().get_object_list().count()
        else:
            return super().total()


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


class ActionChoices(TextChoices):
    """
    Class for listing action to be applied to a set of objects

    Each attribute should either be name of a function found in
    the corresponding ActionHandler, or a 2-tuple containing
    the function name and a label for the action.
    """
    __empty__ = '---------'  # noop action


class ActionHandler(object):
    """
    Class for applying action to a set of objects

    Each function name should also appear in the corresponding ActionChoices.
    """
    pass


class ListActionMixin(object):
    # mixin to be used with ListModelView
    template_name = 'material/frontend/views/filter_list.html'
    action_choices = ActionChoices
    action_handler = ActionHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.list_display and self.list_display[0] != 'pk':
            self.list_display = ['pk', *self.list_display]

    def get_datatable_config(self):
        config = {
            'columnDefs': [{
                'targets': 0,
                'checkboxes': {
                    'selectRow': True,
                    'selectAllRender': render_to_string(
                        'datatable/dt_checkbox.html'),
                },
                'render': -1,  # invalid value, to force using defaultContent
                'defaultContent': render_to_string('datatable/dt_checkbox.html')
            }],
            'select': {
                'style': 'multi+shift',
                'selector': 'td:first-child input[type=checkbox] + span',
            },
        }
        config.update(super().get_datatable_config())
        return config

    def get_list_display_links(self, list_display):
        list_display_links = super().get_list_display_links(list_display)
        if list_display_links[0] == 'pk':
            list_display_links.pop(0)
        if len(list_display_links) == 0 and len(list_display) >= 2:
            return list_display[1]
        return list_display_links

    def get_context_data(self, **kwargs):
        if self.action_choices and hasattr(self.action_choices, 'choices'):
            class ActionForm(forms.Form):
                action = forms.ChoiceField(
                    choices=self.action_choices.choices)

                class Media:
                    js = ['js/action_form.js']

            kwargs["action_form"] = ActionForm()
        return super().get_context_data(**kwargs)

    def handle_action(self, params):
        pk_list = params.getlist("pk[]")
        chosen_action = params["action"]
        if chosen_action in self.action_choices.values:
            chosen_func = getattr(self.action_handler(), chosen_action)
            chosen_func(pk_list)

    def post(self, request, *args, **kwargs):
        submit_type = self.request.POST.get("submit_type", [])
        if "action" in submit_type:
            self.handle_action(self.request.POST)
            return HttpResponseRedirect("./")
        return super().post(request, *args, **kwargs)


class DeletedListModelView(ListModelView):
    template_name_suffix = '_deleted_list'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.all(force_visibility=DELETED_ONLY_VISIBLE)

    def get_template_names(self):
        template_list = super().get_template_names()
        if template_list[-1] == 'material/frontend/views/list.html':
            template_list[-1] = 'material/frontend/views/deleted_list.html'
        return template_list

    def get_list_display_links(self, list_display):
        return []


class DeletedListMixin(object):
    # mixin to be used with ModelViewSet
    deleted_list_view_class = DeletedListModelView

    def get_deleted_list_view(self):
        """Function view for objects deleted_list."""
        return self.deleted_list_view_class.as_view(
            **self.get_deleted_list_view_kwargs())

    def get_deleted_list_view_kwargs(self, **kwargs):
        """Configuration arguments for deleted_list view.

        May not be called if `get_deleted_list_view` is overridden.
        """
        result = {
            'list_display': self.list_display,
            'list_display_links': self.list_display_links,
            'ordering': self.ordering
        }
        result.update(kwargs)
        return self.filter_kwargs(self.deleted_list_view_class, **result)

    @property
    def deleted_list_view(self):
        """Triple (regexp, view, name) for deleted_list view url config."""
        return [
            '^deleted/$',
            self.get_deleted_list_view(),
            '{model_name}_deleted_list'
        ]
