"""Model data from the HouseCanary API.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import base64
import logging
from typing import Any, Type

# django packages
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

# third party
import requests
from requests.auth import HTTPBasicAuth
from requests.models import Response

logger = logging.getLogger(
    __name__ if __name__ != "__main__" else "canary_core.hc_api_connector.models"
)
User: Type[models.Model] = get_user_model()


class BasicAPIClient(models.Model):
    """Provide a client that uses basic authorization for API access.

    This model can be extracted to a common app should the time come for supporting
    additional APIs.
    """

    #: Child classes may override this property to change the client's authentication
    #: requirements
    AuthClass = HTTPBasicAuth

    credential_id = models.CharField(
        max_length=256,
        unique=True,
        help_text=_(
            "store the `{username}` portion of the "
            "`Authorization: Basic {username}:{password}` header"
        ),
    )
    credential_secret = models.CharField(
        max_length=256,
        help_text=_(
            "store the `{username}` portion of the "
            "`Authorization: Basic {username}:{password}` header"
        ),
    )

    host = models.URLField(
        help_text=_("the scheme, hostname, and port of the API server")
    )

    # ref: https://stackoverflow.com/a/4669755/1415275
    path = models.CharField(
        max_length=256,
        validators=[
            validators.RegexValidator(r"^/?[a-zA-Z0-9_.-]*(/[a-zA-Z0-9_.-]+)*\Z")
        ],
        help_text=_("the URL providing the property data"),
    )

    @property
    def auth_header(self) -> dict[str, bytes]:
        """Provide the HTTP_AUTHORIZATION header for this client.

        Returns:
            dict[str,str]: [description]
        """
        base64_creds = base64.b64encode(
            f"{self.credential_id}:{self.credential_secret}".encode("utf-8")
        )
        return {"HTTP_AUTHORIZATION": b"Basic " + base64_creds}

    def get(self, **params: Any) -> Response:
        """Send a GET request to retrieve property data from this API client.

        Args:
            **params (Any): query string parameters to include with the GET request

        Returns:
            Response: the response object from the GET request.
        """
        return requests.get(
            url="/".join(
                [str(self.host).removesuffix("/"), str(self.path).removeprefix("/")]
            ),
            params=params,
            auth=self.AuthClass(self.credential_id, self.credential_secret),
        )


class Property(models.Model):
    """Model property data retrieved from the HouseCanary API.

    This model is extensible and can be reused for additional APIs in the future. When
    integrating with future APIs:
        - generate a new Django app: canary_core.api_client
        - refactor this model to be stored in the new app
        - remove any HouseCanary API-specific fields
        - import the base model from the new app, and extend it here for HouseCanary
    """

    class SewageType(models.TextChoices):
        """Enumerate the sewage type choices retrieved from HouseCanary."""

        NONE = "NO", _("None")
        MUNICIPAL = "MU", _("Municipal")
        STORM = "ST", _("Storm")
        SEPTIC = "SE", _("Septic")
        YES = "YS", _("Yes")

    apiclient = models.ForeignKey(
        to=BasicAPIClient,
        on_delete=models.SET_NULL,
        null=True,
        help_text=_("The API client provividing information for this property"),
    )
    owners = models.ManyToManyField(
        to=User,
        related_name="properties",
        swappable=True,
        help_text=_(
            "these users own the property or act on behalf of the property owner; they "
            "are authorized to access sensitive information about the property"
        ),
    )

    # TODO: migrate to using AddressField from `django-address` some day
    identifier = models.JSONField(
        default=dict,
        help_text=_(
            "store address information as JSON for use with the HouseCanary API"
        ),
    )
    assessment_date = models.DateField(
        help_text=_("the date at which the property was assessed")
    )
    sewage_type = models.CharField(
        max_length=2, choices=SewageType.choices, default=SewageType.NONE
    )
    other_data = models.JSONField(default=dict, verbose_name=_("Other Data"))

    class Meta:
        """Specify the plural name."""

        verbose_name_plural = _("Properties")
