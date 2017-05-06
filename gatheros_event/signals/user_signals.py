from builtins import hasattr

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from gatheros_event.acl import gatheros_user_context


@receiver(user_logged_in, sender=User)
def add_user_context( user, request, **_ ):
    if request.path == '/admin/login/' or not hasattr(user, 'person'):
        return

    gatheros_user_context.update_user_context(request)


@receiver(user_logged_out, sender=User)
def destroy_user_context( request, **_ ):
    if request.path == '/admin/login/':
        return

    session = request.session
    if 'user_context' in session:
        del request.session['user_context']
        request.session.modified = True