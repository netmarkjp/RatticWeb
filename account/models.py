import uuid
import hmac

from django.db import models
from django import forms
from django.forms import ModelForm, SelectMultiple
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.db.models import F
from django.utils import timezone

from tastypie.compat import AUTH_USER_MODEL
from datetime import timedelta

from cred.models import Tag

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

from django.conf import settings
from Crypto.Cipher import AES
import base64
import re


class LDAPPassChangeForm(SetPasswordForm):
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def clean_old_password(self):
        from django_auth_ldap.backend import LDAPBackend

        old_password = self.cleaned_data["old_password"]
        u = LDAPBackend().authenticate(self.user.username, old_password)
        if u is None:
            raise forms.ValidationError(_("Incorrect password"))
        return old_password

    def save(self):
        old_password = self.cleaned_data["old_password"]
        new_password = self.cleaned_data["new_password1"]

        conn = self.user.ldap_user._get_connection()
        conn.simple_bind_s(self.user.ldap_user.dn, old_password.encode('utf-8'))
        conn.passwd_s(self.user.ldap_user.dn, old_password.encode('utf-8'), new_password.encode('utf-8'))

        return self.user


LDAPPassChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    items_per_page = models.IntegerField(verbose_name=_('Items per page'), default=25)
    favourite_tags = models.ManyToManyField(Tag, verbose_name=_('Favourite tags'), blank=True)
    password_changed = models.DateTimeField(default=now)

    def __unicode__(self):
        return self.user.username


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'password_changed',)
        widgets = {
            'favourite_tags': SelectMultiple(attrs={'class': 'selectize-multiple'}),
        }


# Attach the UserProfile object to the User
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@receiver(pre_save, sender=User)
def user_save_handler(sender, instance, **kwargs):
    try:
        olduser = User.objects.get(id=instance.id)
    except User.DoesNotExist:
        return
    if olduser.password != instance.password:
        p = instance.profile
        p.password_changed = now()
        p.save()


class ApiKey(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, related_name='rattic_api_key')
    key = models.CharField(max_length=128, blank=True, default='', db_index=True)
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=now)
    expires = models.DateTimeField(default=now)

    @classmethod
    def expired(kls, user):
        return ApiKey.objects.filter(user=user, expires__gt=F("created")).filter(expires__lt=timezone.now())

    @classmethod
    def delete_expired(kls, user):
        for gone in kls.expired(user):
            gone.delete()

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()

    @property
    def has_expiry(self):
        return self.expires > self.created


class ApiKeyForm(ModelForm):
    class Meta:
        model = ApiKey
        exclude = ('user', 'key', 'active', 'created', 'expires')

    def save(self):
        if self.instance.expires < self.instance.created + timedelta(minutes=1):
            self.instance.expires = self.instance.created
        return super(ApiKeyForm, self).save()


class TwoFactorAuthSecret(models.Model):
    PADDING_CHARACTER = "\0"

    user = models.ForeignKey(AUTH_USER_MODEL)
    name = models.CharField(max_length=255)
    encrypted_secret = models.TextField()
    created = models.DateTimeField(default=now)

    def __unicode__(self):
        return u"%s for %s" % (self.name, self.user)

    def set_secret(self, plain_secret, secret_key):
        secret_key = TwoFactorAuthSecret.normalize_secret_key(secret_key)

        aes = AES.new(secret_key, AES.MODE_CBC,
                      TwoFactorAuthSecret.get_initial_vector())
        encrypted = aes.encrypt(plain_secret)
        b64_encrypted = base64.b64encode(encrypted)
        self.encrypted_secret = b64_encrypted

    def get_plain_secret(self, secret_key):
        secret_key = TwoFactorAuthSecret.normalize_secret_key(secret_key)
        aes = AES.new(secret_key, AES.MODE_CBC,
                      TwoFactorAuthSecret.get_initial_vector())
        return TwoFactorAuthSecret.unpad(aes.decrypt(base64.b64decode(self.encrypted_secret)))

    @staticmethod
    def normalize_secret_key(secret_key):
        # secret_key must be 16, 24, or 32 bytes long
        length = len(secret_key)
        if length > 32:
            # FIXME error
            raise Exception("secret_key too long")
        elif length > 24:
            secret_key = TwoFactorAuthSecret.pad(secret_key, 32)
        elif length > 16:
            secret_key = TwoFactorAuthSecret.pad(secret_key, 24)
        elif length > 0:
            secret_key = TwoFactorAuthSecret.pad(secret_key, 16)
        else:
            # FIXME error
            raise Exception("empty secret_key")
        return secret_key

    @staticmethod
    def get_initial_vector():
        # inital_vector must be 16 bytes long
        inital_vector = TwoFactorAuthSecret.pad(settings.SECRET_KEY[:16])

        # FIXME adjust length
        inital_vector = TwoFactorAuthSecret.pad(inital_vector)

        return inital_vector

    @staticmethod
    def block_length(text, block_size=AES.block_size):
        if not isinstance(text, str):
            text = str(text)
        div = int(len(text) / block_size)
        mod = len(text) % block_size
        block_length = div
        if mod > 0:
            block_length += 1
        return block_length

    @staticmethod
    def pad(text, block_size=AES.block_size):
        if not isinstance(text, str):
            text = str(text)
        _block_length = TwoFactorAuthSecret.block_length(text, block_size)
        pad_length = block_size * _block_length - len(text)
        return text + TwoFactorAuthSecret.PADDING_CHARACTER * pad_length

    @staticmethod
    def unpad(text):
        return re.sub("{}+$".format(TwoFactorAuthSecret.PADDING_CHARACTER), "", text)


class TwoFactorAuthSecretForm(ModelForm):
    class Meta:
        model = TwoFactorAuthSecret
        exclude = ("user", "encrypted_secret", "created")


admin.site.register(UserProfile)
