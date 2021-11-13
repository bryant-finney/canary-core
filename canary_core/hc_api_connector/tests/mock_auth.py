"""TODO: write synopsis.

.. moduleauthor:: Bryant Finney <finneybp@gmail.com>
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import logging
from typing import Optional

# django packages
from django.http.request import HttpRequest
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication

# local
from canary_core.hc_api_connector.models import BasicAPIClient

logger = logging.getLogger(__name__)


class GenericAPIAuthentication(BasicAuthentication):
    """Mock out the authentication class used by the API client."""

    def authenticate_credentials(
        self,
        credential_id: str | bytes,
        credential_secret: str | bytes,
        request: Optional[HttpRequest] = None,
    ) -> tuple[BasicAPIClient, None]:
        """Override the parent class's method to reference the BasicAPIClient model.

        Args:
            credential_id (str | bytes): the ID (username) part of the credential
            credential_secret (str): the secret key (password) part of the credential
            request (Optional[HttpRequest]): The incoming request to maintain
                compatibility with parent; defaults to None.

        Raises:
            AuthenticationFailed: raised if the credentials don't match an API client

        Returns:
            tuple[BasicAPIClient, None]: returns the ``BasicAPIClient`` record
        """
        credentials = {
            "credential_id": credential_id,
            "credential_secret": credential_secret,
        }
        try:
            client = BasicAPIClient.objects.get(**credentials)
        except BasicAPIClient.DoesNotExist:
            raise exceptions.AuthenticationFailed(detail="Invalid credentials")

        client.is_authenticated = True
        return (client, None)


logger.debug("imported module %s", __name__)
