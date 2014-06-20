from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from registration.signals import user_registered

from registration_email_only.utils import user_to_activation_key
from registration_email_only.backends.views import RegisterView


class RegisterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.req = self.factory.get(reverse('registration_register'))
        SessionMiddleware().process_request(self.req)
        self.b = RegisterView()

    def test_register_no_email(self):
        with self.assertRaises(ValueError):
            self.b.register(self.req)

    def test_unusable_password(self):
        u = self.b.register(self.req, email='this@that.com')
        self.assertFalse(u.has_usable_password())

    def test_signal_sent(self):
        signal_user = set()
        def user_registered_signal_handler(sender, request, user, **kwargs):
            signal_user.add(user)
        user_registered.connect(
            user_registered_signal_handler)
        u = self.b.register(self.req, email='this@that.com')
        self.assertIn(u, signal_user)

    def test_logged_in(self):
        signal_user = set()
        def login_signal_handler(sender, request, user, **kwargs):
            signal_user.add(user)
        user_logged_in.connect(login_signal_handler)
        u = self.b.register(self.req, email='this@that.com')
        self.assertIn(u, signal_user)

    def test_email_sent(self):
        self.b.register(self.req, email='this@that.com')
        self.assertEqual(len(mail.outbox), 1)


class ActivateTests(TestCase):
    def setUp(self):
        factory = RequestFactory()
        request = factory.get(reverse('registration_register'))
        SessionMiddleware().process_request(request)
        self.user = RegisterView().register(request, email='this@that.com')
        self.user.set_unusable_password()
        self.activation_key = user_to_activation_key(self.user)

    def test_form(self):
        response = self.client.get(reverse('registration_activate', args=(self.activation_key, )))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_valid_form(self):
        self.assertFalse(self.user.has_usable_password())
        response = self.client.post(reverse('registration_activate', args=(self.activation_key, )), {
            'activation_key': self.activation_key,
            'username': 'username',
            'password': 'pass'
        })
        self.assertRedirects(response, reverse('registration_activation_complete'))
        user = User.objects.get(username='username')
        self.assertTrue(user.has_usable_password())
