from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class BootstrapFormMixin:
    """Apply Bootstrap 5 classes to all form fields."""

    def apply_bootstrap_classes(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({"class": "form-check-input"})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": "form-select"})
            else:
                widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(UserCreationForm, BootstrapFormMixin):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()