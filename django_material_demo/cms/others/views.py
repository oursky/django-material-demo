from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from components.widgets.nativedate import NativeDate


class CustomizedComponentForm(forms.Form):
    native_date = forms.DateField(label='Native Date Input', required=False, widget=NativeDate)


@method_decorator(staff_member_required(login_url='login'), name='dispatch')
class CustomizedComponentView(FormView):
    form_class = CustomizedComponentForm
    template_name = 'cms/others.html'
