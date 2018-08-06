from django.forms import (
    Form, CharField, PasswordInput, EmailField, Textarea, TextInput)
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

class AnyUserForm(Form):
    captcha = ReCaptchaField(widget=ReCaptchaWidget(theme='dark'))

class MainUserForm(Form):
    username = CharField(max_length=100, min_length=5)
    password = CharField(
        max_length=100, min_length=5,
        widget=PasswordInput)
    email = EmailField()
    captcha = ReCaptchaField(widget=ReCaptchaWidget(theme='dark'))

class MainLoginForm(Form):
    email = EmailField()
    password = CharField(
    max_length=100, min_length=5,
    widget=PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaWidget(theme='dark'))

class ChangePasswordForm(Form):
    password = CharField(
    max_length=100, min_length=5,
    widget=PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your new password ...'
    }))

class TextingForm(Form):
    title = CharField(
        max_length=200,
        min_length=5,
        widget=TextInput(attrs={
            'class': 'form-control toAddText'}))
    text = CharField(
        max_length=1999,
        min_length=5,
        widget=Textarea(attrs={
            'id': 'texting',
            'style': 'width: 100%;',
            'class': 'form-control'}))

class SearchForm(Form):
    text = CharField(
        max_length=300,
        min_length=2,
        widget=TextInput(attrs={
            'class': 'form-control header-font',
            'placeholder': 'Keywords to search for ...'}))