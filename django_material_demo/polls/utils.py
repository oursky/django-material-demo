from django.db import models
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from material.frontend.views import DetailModelView


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


class CustomDetailModelView(DetailModelView):
    # Modified from following to support displaying fields with multiple values
    # https://github.com/viewflow/django-material/blob/master/material/frontend/views/detail.py#L27
    def get_object_data(self):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        for field in self.object._meta.get_fields():
            if isinstance(field, models.AutoField):
                continue
            elif field.auto_created:  # reverse relations are excluded here
                continue
            else:
                choice_display_attr = "get_{}_display".format(field.name)
            if hasattr(self.object, choice_display_attr):
                value = getattr(self.object, choice_display_attr)()
            else:
                value = getattr(self.object, field.name)

            if value is not None:
                if isinstance(value, models.Manager):
                    value_list = value.all()
                    if len(value_list):
                        yield (field.verbose_name.title(),
                               get_html_list(value_list))
                else:
                    yield (field.verbose_name.title(), value)
