from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from registration_email_only.utils import default_create_username, get_username_creator, userid_to_uid, uid_to_userid, user_to_activation_key, \
    activation_key_to_user


class GetUsernameCreatorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.req = self.factory.get(reverse('registration_register'))
        SessionMiddleware().process_request(self.req)

    def test_default_create_username(self):
        req1 = self.req
        req2 = self.factory.get(reverse('registration_register'))
        username = default_create_username(req1, 'this@that.com')
        self.assertNotEqual(username, default_create_username(req2, 'this@that.com'))
        self.assertEqual(len(username), 30)

    def test_no_username_creator(self):
        self.assertEqual(get_username_creator(), default_create_username)

    @override_settings(REGISTRATION_EMAIL_ONLY_USERNAME_CREATOR='not.a.module')
    def test_bad_username_creator_string(self):
        with self.assertRaises(ImproperlyConfigured):
            get_username_creator()

    @override_settings(REGISTRATION_EMAIL_ONLY_USERNAME_CREATOR=object())
    def test_bad_type(self):
        with self.assertRaises(ImproperlyConfigured):
            get_username_creator()


class UtilsTests(TestCase):
    def test_uid_userid_conversion_even_digits(self):
        userid = 23
        cycled_userid = uid_to_userid(userid_to_uid(userid))
        self.assertEqual(userid, cycled_userid)

    def test_uid_userid_conversion_odd_digits(self):
        userid = 3
        cycled_userid = uid_to_userid(userid_to_uid(userid))
        self.assertEqual(userid, cycled_userid)

    def test_activation_key_cycle(self):
        u = User.objects.create_user('username', 'em@il.com')
        activation_key = user_to_activation_key(u)
        retrieved_user = activation_key_to_user(activation_key)
        self.assertEqual(u, retrieved_user)
