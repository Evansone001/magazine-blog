from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import widgets

from . import utils
from .models import BlogUser


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"})
        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"})


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"})
        self.fields['email'].widget = widgets.EmailInput(
            attrs={'placeholder': "email", "class": "form-control"})
        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"})
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': "repeat password", "class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This mailbox already exists.")
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class ForgetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="new password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': "password"
            }
        ),
    )

    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': "Confirm Password"
            }
        ),
    )

    email = forms.EmailField(
        label='mail',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "mail"
            }
        ),
    )

    code = forms.CharField(
        label='verification code',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': "verification code"
            }
        ),
    )

    def clean_new_password2(self):
        password1 = self.data.get("new_password1")
        password2 = self.data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two passwords do not match")
        password_validation.validate_password(password2)

        return password2

    def clean_email(self):
        user_email = self.cleaned_data.get("email")
        if not BlogUser.objects.filter(
                email=user_email
        ).exists():
            # todo The error message here can determine whether an email address has been registered. If you don’t want to expose it, you can modify it.
            raise ValidationError(
                "The user corresponding to the email address was not found")
        return user_email

    def clean_code(self):
        code = self.cleaned_data.get("code")
        error = utils.verify(
            email=self.cleaned_data.get("email"),
            code=code,
        )
        if error:
            raise ValidationError(error)
        return code


class ForgetPasswordCodeForm(forms.Form):
    email = forms.EmailField(
        label="mailbox number"
    )
