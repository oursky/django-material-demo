from functools import reduce
from operator import or_

from django.db.models import Q
from django_filters import CharFilter, FilterSet
from django_filters.views import FilterView


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
