
"""
URLconf for registration and activation, using the email-only backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration_email_only.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead.

"""
from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
from registration_email_only.backends.views import ActivateView, RegisterView


urlpatterns = patterns('',
                       url(r'^activate/complete/$',
                           TemplateView.as_view(template_name='registration/activation_complete.html'),
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of a more specific
                       # regex because a bad activation key should still get to the
                       # view; that way it can return a sensible "invalid key" message
                       # instead of a confusing 404.
                       url(r'^activate/(?P<activation_key>[\w-]+)/$',
                           ActivateView.as_view(),
                           name='registration_activate'),
                       url(r'^register/$',
                           RegisterView.as_view(),
                           name='registration_register'),
                       url(r'^register/complete/$',
                           TemplateView.as_view(template_name='registration/registration_complete.html'),
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
                       )