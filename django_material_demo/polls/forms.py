from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from material import Layout


class EmailLoginForm(AuthenticationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput)

    layout = Layout('email', 'password')

    error_messages = {
        "invalid_login": (
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": "This account is inactive.",
    }

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None

        # Skip __init__ from AuthenticationForm
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        del self.fields["username"]  # username not used

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"email": "email"},
        )
