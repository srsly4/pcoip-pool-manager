from datetime import timedelta

from django.utils.datetime_safe import datetime
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import ExpirableToken


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = ExpirableToken.objects.get(key=key)
        except self.get_model().DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        # timedelta hardcoded, token is valid for 1 hour, this should change if expiration_time gets implemented
        if datetime.now() > token.last_refresh_datetime + timedelta(hours=1):
            raise exceptions.AuthenticationFailed('Token has expired')
        else:
            token = token.refresh()

        return token.user, token
