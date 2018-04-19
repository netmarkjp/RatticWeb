from django.conf.urls import include, url
from django.conf import settings
from django.contrib.auth.views import logout
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm

from .views import profile, newapikey, deleteapikey, RatticSessionDeleteView
from .views import RatticTFADisableView, RatticTFABackupTokensView
from .views import RatticTFASetupView, RatticTFALoginView
from .views import RatticTFAGenerateApiKey
from .views import TwoFactorAuthSecretIndexView, TwoFactorAuthSecretView, TwoFactorAuthSecretDeleteView, TwoFactorAuthSecretModifyView
from .views import rattic_change_password
from .views import ldap_password_change

from two_factor.views import QRGeneratorView

urlpatterns = [
    url(r'^$', profile, {}, name='profile'),
    url(r'^newapikey/$', newapikey, {}, name='newapikey'),
    url(r'^deleteapikey/(?P<key_id>\d+)/$', deleteapikey, {}, name='deleteapikey'),

    url(r'^logout/$', logout, {
        'next_page': settings.RATTIC_ROOT_URL}, name='logout'),

    # View to kill other sessions with
    url(r'^killsession/(?P<pk>\w+)/', RatticSessionDeleteView.as_view(), name='kill_session'),

    # Two Factor Views
    url(r'^login/$', RatticTFALoginView.as_view(), name='login'),
    url(r'^generate_api_key$', RatticTFAGenerateApiKey.as_view(), name='generate_api_key'),

    url(r'^two_factor/disable/$', RatticTFADisableView.as_view(), name='tfa_disable'),
    url(r'^two_factor/backup/$', RatticTFABackupTokensView.as_view(), name='tfa_backup'),
    url(r'^two_factor/setup/$', RatticTFASetupView.as_view(), name='tfa_setup'),
    url(r'^two_factor/qr/$', QRGeneratorView.as_view(), name='tfa_qr'),

    # Two Factor Secret Views
    url(r"^two_factor_auth_secret/$", TwoFactorAuthSecretIndexView.as_view(), name="two_factor_auth_secret_index"),
    url(r"^two_factor_auth_secret/(?P<id>\w+)/$", TwoFactorAuthSecretView.as_view(), name="two_factor_auth_secret_id"),
    url(r"^two_factor_auth_secret/(?P<id>\w+)/delete/$", TwoFactorAuthSecretDeleteView.as_view(), name="two_factor_auth_secret_id_delete"),
    url(r"^two_factor_auth_secret/(?P<id>\w+)/modify/$", TwoFactorAuthSecretModifyView.as_view(), name="two_factor_auth_secret_id_modify"),
]

if settings.GOAUTH2_ENABLED:
    urlpatterns += [
        url(r'', include("social_django.urls", namespace="social")),
    ]

# URLs we don't want enabled with LDAP
if not settings.LDAP_ENABLED:
    urlpatterns += [
        url(r'^reset/$', password_reset,
            {
                'post_reset_redirect': '/account/reset/done/',
                'template_name': 'password_reset.html'
            },
            name="password_reset"
        ),

        url(r'^reset/done/$', password_reset_done, {
            'template_name': 'password_reset_done.html'},
            name="password_reset_done"
        ),

        url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
            'post_reset_redirect': '/',
            'template_name': 'password_reset_confirm.html'},
            name="password_reset_confirm"
        ),

        url(r'^changepass/$', rattic_change_password, {
            'post_change_redirect': '/account/',
            'template_name': 'account_changepass.html'}, name='password_change')
    ]

# URLs we do want enabled with LDAP
if settings.LDAP_ENABLED and settings.AUTH_LDAP_ALLOW_PASSWORD_CHANGE:
    urlpatterns += [
        url(r'^changepass/$', ldap_password_change, {}, name='password_change')
    ]
