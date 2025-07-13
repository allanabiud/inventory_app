from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.contrib.auth.models import User


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            FloatingField("username"),
            FloatingField("password"),
            Submit("submit", "Sign In", css_class="btn btn-success w-100"),
        )


class CustomUserCreationForm(BaseUserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="First Name")
    last_name = forms.CharField(max_length=150, required=True, label="Last Name")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.pop("autofocus", None)

        for field in self.fields.values():
            if field.help_text:
                field.widget.attrs["data-bs-toggle"] = "tooltip"
                field.widget.attrs["data-bs-trigger"] = "focus"
                field.widget.attrs["data-bs-html"] = "true"
                field.widget.attrs["data-bs-placement"] = "right"
                field.widget.attrs["title"] = field.help_text
                field.help_text = ""

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column(FloatingField("first_name"), css_class="col-md-6"),
                Column(FloatingField("last_name"), css_class="col-md-6"),
                css_class="g-2",
            ),
            FloatingField("username"),
            FloatingField("password1"),
            FloatingField("password2"),
            Submit("submit", "Sign Up", css_class="btn btn-success w-100"),
        )
