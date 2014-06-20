from django import forms
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from registration_email_only.utils import activation_key_to_user


class RegistrationForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """ Ensure that the supplied email address is unique. """
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exists():
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']


class ActivationForm(forms.Form):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
                                help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
                                error_message=_("This value must contain only letters, numbers and underscores."))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label=_("Password"))
    activation_key = forms.CharField(widget=forms.HiddenInput())
    next = forms.URLField(required=False, widget=forms.HiddenInput())

    def clean_username(self):
        """ Ensure that the supplied username is unique. """
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def _get_user(self):
        return activation_key_to_user(self.cleaned_data['activation_key'])

    def activate(self, request):
        user = self._get_user()
        if not user:
            return False
        password = self.cleaned_data['password']
        user.username = self.cleaned_data['username']
        user.set_password(password)
        user.save()
        self.login_user(request, user, password)
        return user

    def login_user(self, request, user, password):
        auth_user = authenticate(username=user.username, password=password)
        login(request, auth_user)
