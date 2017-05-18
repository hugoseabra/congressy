"""Gatheros utility for testing with user authentication"""

from django.contrib.auth.models import User


class TestcaseUserBackend(object):
    """TestcaseUserBackend to login using only user object, with no password"""

    # noinspection PyMethodMayBeStatic
    def authenticate(self, testcase_user=None):
        """Authenticates using testcase"""
        return testcase_user

    # noinspection PyMethodMayBeStatic
    def get_user(self, user_id):
        """Gets user from id"""
        return User.objects.get(pk=user_id)
