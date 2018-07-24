from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm as AuthForm

LOGIN_SUPERUSER_ONLY = getattr(settings, 'LOGIN_SUPERUSER_ONLY', False)


class AuthenticationForm(AuthForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """

    def add_captcha(self):
        self.fields['captcha'] = CaptchaField()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if LOGIN_SUPERUSER_ONLY is True and not user.is_superuser:
            raise forms.ValidationError(
                "Somente usuários com permissões adquadas podem entrar neste"
                " ambiente.",
                code='not-superuser',
            )
