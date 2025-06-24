from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
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
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

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
            FloatingField("username"),
            FloatingField("password1"),
            FloatingField("password2"),
            Submit("submit", "Sign Up", css_class="btn btn-success w-100"),
        )
