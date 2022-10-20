from django.core.exceptions import ValidationError
from django.forms import widgets
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import (ModelFormMixin, ProcessFormView,
                                       UpdateView)
from django_superform import ModelFormField


class NestedModelFormField(ModelFormField):
    def get_instance(self, form, name):
        if form._meta.model != self.form_class._meta.model:
            raise ValueError('Field model must be same as the form model')
        return form.instance


class RangeInput(widgets.Input):
    input_type = 'range'

    class Media:
        js = ['js/range_input.js']


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
            val = self[field_name].data
            try:
                # format value by form field
                return self[field_name].field.to_python(val)
            except ValidationError:
                return val
        else:
            # use initial value
            return self.initial.get(field_name)
