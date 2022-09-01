from django.forms import ModelForm
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


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
