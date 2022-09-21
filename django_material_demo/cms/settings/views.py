from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import model_to_dict
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from .models import Settings


class SettingsForm(forms.Form):
    primary_color = forms.CharField(label='Primary color', required=False)
    primary_color_light = forms.CharField(
        label='Primary color light', required=False)
    primary_color_dark = forms.CharField(
        label='Primary color dark', required=False)
    secondary_color = forms.CharField(label='Secondary color', required=False)
    secondary_color_light = forms.CharField(
        label='Secondary color light', required=False)
    success_color = forms.CharField(label='Success color', required=False)
    error_color = forms.CharField(label='Error color', required=False)
    link_color = forms.CharField(label='Link color', required=False)


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class SettingsView(FormView):
    form_class = SettingsForm
    template_name = 'cms/settings.html'

    def get_initial(self):
        return model_to_dict(Settings(session=self.request.session))

    def form_valid(self, form):
        settings = Settings(session=self.request.session)
        for k, v in form.cleaned_data.items():
            setattr(settings, k, v)

        settings.save()
        return redirect('settings:index')
