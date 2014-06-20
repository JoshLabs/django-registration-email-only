from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import FormView
from registration.signals import user_registered
from registration.backends.default.views import RegistrationView
from registration_email_only.forms import ActivationForm, RegistrationForm
from registration_email_only.utils import create_user_and_password, send_activation_email, activation_key_to_user, get_site


class RegisterView(RegistrationView):
    form_class = RegistrationForm

    def register(self, request, email=None):
        """ Create user; log in; send activation email

        Here's how it works:
         - Create a user with a random password
         - log them in (requires a password to be set)
         - sets the password to be unusable
         - send an email to complete registration

        This function assumes that the form has already been validated,
        meaning the email has already been verified as unique.
        """
        if email is None:
            raise ValueError('email cannot be None')
        user, password = create_user_and_password(request, email)
        # log in
        auth_user = authenticate(username=user.username, password=password)
        assert auth_user == user
        login(request, auth_user)
        user.set_unusable_password()
        user.save()
        # get site
        site = get_site(request)
        send_activation_email(user, site)
        user_registered.send(
            sender=self.__class__,
            user=user,
            request=request
        )
        return user


class ActivateView(FormView):
    """
    Activate a user's account by setting password and username
    """
    form_class = ActivationForm
    success_url = None
    template_name = 'registration/activate_form.html'

    def dispatch(self, request, *args, **kwargs):
        user = activation_key_to_user(kwargs.get('activation_key'))
        if not user:
            raise Http404()
        else:
            return super(ActivateView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(ActivateView, self).get_initial()
        initial.update({'activation_key': self.kwargs['activation_key']})
        return initial

    def form_valid(self, form):
        form.activate(self.request)
        self.success_url = form.cleaned_data['next'] if form.cleaned_data['next'] else reverse('registration_activation_complete')
        return super(ActivateView, self).form_valid(form)
