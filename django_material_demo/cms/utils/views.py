from functools import reduce
from operator import or_

from django.db.models import Q
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django_filters import CharFilter, FilterSet
from django_filters.views import FilterView


def get_html_list(arr):
    """Generate a HTML unordered list from an iterable

    Return an empty string instead when iterable is empty
    """
    if len(arr) == 0:
        return ''

    #TODO: replace with template
    value_list = [conditional_escape(x) for x in arr]
    value_list_html = mark_safe(
        '<ul>'
        + ''.join('<li>' + x + '</li>' for x in value_list)
        + '</ul>')
    return value_list_html


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
