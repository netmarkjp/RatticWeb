# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from account.models import ApiKey, ApiKeyForm
from account.models import TwoFactorAuthSecret
from models import UserProfileForm, LDAPPassChangeForm

from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib.auth.views import password_change
from django.contrib.auth.forms import SetPasswordForm
from django.utils import timezone

from user_sessions.views import SessionDeleteView
from two_factor.utils import default_device
from two_factor.views import DisableView, BackupTokensView, SetupView, LoginView
from datetime import timedelta
import uuid

from django import forms
import pyotp
import zbar  # TODO Fix Segmentation fault at MacOSX
import PIL.Image
import urlparse


@login_required
def rattic_change_password(request, *args, **kwargs):
    print request.user
    if request.user.has_usable_password():
        # If a user is changing their password
        return password_change(request, *args, **kwargs)
    else:
        # If a user is setting an initial password
        kwargs['password_change_form'] = SetPasswordForm
        return password_change(request, *args, **kwargs)


@login_required
def profile(request):
    # Delete our expired keys
    ApiKey.delete_expired(user=request.user)

    # Get a list of the users API Keys
    keys = ApiKey.objects.filter(user=request.user)
    try:
        backup_tokens = request.user.staticdevice_set.all()[0].token_set.count()
    except IndexError:
        backup_tokens = 0

    # Get a list of the users current sessions
    sessions = request.user.session_set.filter(expire_date__gt=now())

    # Get the current session key
    session_key = request.session.session_key

    # Process the form if we have data coming in
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=request.user.profile)

    # TwoFactorAuthSecret
    two_factor_auth_secrets = TwoFactorAuthSecret.objects.filter(user=request.user)

    # Show the template
    return render(request, 'account_profile.html', {
        'keys': keys,
        'sessions': sessions,
        'session_key': session_key,
        'form': form,
        'user': request.user,
        'default_device': default_device(request.user),
        'backup_tokens': backup_tokens,
        'two_factor_auth_secrets': two_factor_auth_secrets,
    })


@login_required
def newapikey(request):
    if request.method == 'POST':
        newkey = ApiKey(user=request.user, active=True)
        form = ApiKeyForm(request.POST, instance=newkey)
        if form.is_valid():
            form.save()
        return render(request, 'account_viewapikey.html', {'key': newkey})
    else:
        form = ApiKeyForm()

    return render(request, 'account_newapikey.html', {'form': form})


@login_required
def deleteapikey(request, key_id):
    key = get_object_or_404(ApiKey, pk=key_id)

    if key.user != request.user:
        raise Http404

    if request.method == 'POST':
        key.delete()
        return HttpResponseRedirect(reverse('account.views.profile'))

    return render(request, 'account_deleteapikey.html', {'key': key})


# Stolen from django.contrib.auth.views
# modifed to support LDAP errors
@sensitive_post_parameters()
@login_required
def ldap_password_change(request,
                    template_name='account_changepass.html',
                    post_change_redirect='/account/',
                    password_change_form=LDAPPassChangeForm,
                    current_app=None, extra_context=None):
    import ldap

    if post_change_redirect is None:
        post_change_redirect = reverse('account.views.rattic_change_password_done')
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            try:
                form.save()
                return HttpResponseRedirect(post_change_redirect)
            except ldap.LDAPError as e:
                return render(request, 'account_ldaperror.html', {
                    'desc': e.message['desc'],
                    'info': e.message['info'],
                })
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class RatticSessionDeleteView(SessionDeleteView):
    def get_success_url(self):
        return reverse('account.views.profile')


class RatticTFADisableView(DisableView):
    template_name = 'account_tfa_disable.html'
    redirect_url = 'account.views.profile'


class RatticTFABackupTokensView(BackupTokensView):
    template_name = 'account_tfa_backup_tokens.html'
    redirect_url = 'tfa_backup'
    success_url = 'tfa_backup'


class RatticTFASetupView(SetupView):
    template_name = 'account_tfa_setup.html'
    qrcode_url = 'tfa_qr'
    redirect_url = 'account.views.profile'
    success_url = 'account.views.profile'


class RatticTFALoginView(LoginView):
    template_name = 'account_tfa_login.html'


class RatticTFAGenerateApiKey(LoginView):
    def get(self, request, *args, **kwargs):
        res = HttpResponse()
        res.set_cookie("csrftoken", request.META['CSRF_COOKIE'])
        res.status_code = 405
        return res

    def render(self, form=None, **kwargs):
        if self.steps.current == 'token':
            device = self.get_device()
            device.generate_challenge()
            res = HttpResponse(device.persistent_id)
            res.status_code = 400
            return res

    def done(self, form_list, **kwargs):
        login(self.request, self.get_user())
        ApiKey.delete_expired(user=self.request.user)

        newkey = ApiKey(user=self.request.user, active=True, expires=timezone.now() + timedelta(minutes=5))
        form = ApiKeyForm({"name": uuid.uuid1()}, instance=newkey)
        if form.is_valid():
            form.save()

        res = HttpResponse(newkey.key)
        res.status_code = 200
        return res


class QRImageUploadForm(forms.Form):
    secret_key = forms.CharField(max_length=255, required=True)
    qr_image_file = forms.FileField(required=True)


class TwoFactorAuthSecretIndexView(TemplateView):
    template_name = "two_factor_auth_secret_index.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response({"form": QRImageUploadForm()})

    def post(self, request, *args, **kwargs):
        # QRコードをアップロードしてもらって解析
        form = QRImageUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response({"form": form})
        parsed = parse_qr_image(request.FILES["qr_image_file"])
        name = parsed[0]
        plain_secret = parsed[1]

        # 暗号化して保存
        obj = TwoFactorAuthSecret(user=request.user, name=name)
        obj.set_secret(plain_secret, request.POST.get("secret_key"))
        obj.save()

        # 成功したら個別画面にリダイレクト
        return HttpResponseRedirect(reverse("two_factor_auth_secret_id", args=[obj.id]))


class SecretForm(forms.Form):
    secret_key = forms.CharField(max_length=255, required=True)


class TwoFactorAuthSecretView(TemplateView):
    template_name = "two_factor_auth_secret.html"

    def get(self, request, *args, **kwargs):
        id_ = kwargs.get("id")  # id from url

        secrets = TwoFactorAuthSecret.objects.filter(id=id_, user=request.user)
        if len(secrets) == 0:
            raise Http404
        secret = secrets[0]

        return self.render_to_response({"secret": secret, "form": SecretForm()})

    def post(self, request, *args, **kwargs):
        id_ = kwargs.get("id")  # id from url

        secrets = TwoFactorAuthSecret.objects.filter(id=id_, user=request.user)
        if len(secrets) == 0:
            raise Http404
        secret = secrets[0]

        form = SecretForm(request.POST)
        if not form.is_valid():
            return self.render_to_response({"secret": secret, "form": form})

        try:
            otp = pyotp.TOTP(secret.get_plain_secret(request.POST.get("secret_key"))).now()
            return self.render_to_response({"secret": secret, "form": form, "otp": otp})
        except Exception as e:
            print(e)
            return self.render_to_response({"secret": secret, "form": form, "otp": "ERROR: Failed to decrypt. Secret key maybe incorrect"})  # TODO error messaging


class TwoFactorAuthSecretDeleteView(TemplateView):
    template_name = "two_factor_auth_secret.html"

    def post(self, request, *args, **kwargs):
        id_ = kwargs.get("id")  # id from url

        secrets = TwoFactorAuthSecret.objects.filter(id=id_, user=request.user)
        if len(secrets) == 0:
            raise Http404
        secret = secrets[0]

        secret.delete()
        return HttpResponseRedirect(reverse("account.views.profile"))


def parse_qr_image(filepath):

    scanner = zbar.ImageScanner()
    scanner.parse_config("enable")
    pil = PIL.Image.open(filepath).convert("L")
    (width, height) = pil.size
    image = zbar.Image(width, height, "Y800", pil.tobytes())
    scanner.scan(image)

    name = ""
    plain_secret = ""
    for symbol in image:
        parsed = urlparse.urlparse(symbol.data)
        try:
            name = urlparse.parse_qs(parsed.query).get("issuer", [""])[0]
        except Exception as e:
            print(e)
        plain_secret = urlparse.parse_qs(parsed.query).get("secret", [""])[0]

    return (name, plain_secret)
