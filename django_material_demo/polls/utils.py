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
