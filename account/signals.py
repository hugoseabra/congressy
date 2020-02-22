from django.contrib.auth.signals import user_logged_out
from rest_framework.authtoken.models import Token


def logout_token_deletion(user, request):
    try:
        token = Token.objects.get(user_id=user.pk)
        token.delete()
    except Token.DoesNotExist:
        pass


user_logged_out.connect(logout_token_deletion)
