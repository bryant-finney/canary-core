"""Model data from the HouseCanary API.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import base64
import datetime as dt
import logging
from typing import TYPE_CHECKING, Any, Type

# django packages
from django.contrib.auth import get_user_model
from django.core import validators
from django.db.models import CharField, ForeignKey, ManyToManyField, Model
from django.db.models.deletion import SET_NULL
from django.db.models.enums import TextChoices
from django.db.models.fields import DateField, URLField
from django.db.models.fields.json import JSONField
from django.utils.translation import gettext_lazy as _

# third party
import requests
from requests.auth import HTTPBasicAuth
from requests.models import Response

# TypedDict lives in the `typing` module starting with Python3.8; Python3.7 needs to
#   import it from typing_extensions instead
try:
    # stdlib
    from typing import TypedDict
except ImportError:  # pragma: no cover
    # third party
    from typing_extensions import TypedDict  # pragma: no cover

logger = logging.getLogger(
    __name__ if __name__ != "__main__" else "canary_core.hc_api_connector.models"
)

if TYPE_CHECKING:
    # this branch only executes when `mypy` is performing static analysis

    # stdlib
    from typing import Optional  # noqa: F401  # pragma: no cover

    # django packages
    from django.contrib.auth.models import User  # noqa: I005  # pragma: no cover
    from django.db.models import QuerySet  # noqa: F401  # pragma: no cover
else:
    User: Type[Model] = get_user_model()


class BasicAPIClient(Model):
    """Provide a client that uses basic authorization for API access.

    This model can be extracted to a common app should the time come for supporting
    additional APIs.
    """

    class Meta:
        """Set the verbose/plural names."""

        verbose_name = _("Basic API Client")
        verbose_name_plural = _("Basic API Clients")

    #: Child classes may override this property to change the client's authentication
    #: requirements
    AuthClass = HTTPBasicAuth

    name: "CharField" = CharField(
        max_length=64,
        null=False,
        blank=True,
        help_text=_("friendly name of the API client"),
    )

    credential_id: "CharField" = CharField(
        max_length=256,
        unique=True,
        help_text=_(
            "store the `{username}` portion of the "
            "`Authorization: Basic {username}:{password}` header"
        ),
    )

    credential_secret: "CharField" = CharField(
        max_length=256,
        help_text=_(
            "store the `{username}` portion of the "
            "`Authorization: Basic {username}:{password}` header"
        ),
    )

    host: "URLField" = URLField(
        help_text=_("the scheme, hostname, and port of the API server")
    )

    # ref: https://stackoverflow.com/a/4669755/1415275
    path: "CharField" = CharField(
        max_length=256,
        validators=[
            validators.RegexValidator(r"^/?[a-zA-Z0-9_.-]*(/[a-zA-Z0-9_.-]+)*\Z")
        ],
        help_text=_("the URL providing the property data"),
    )

    def __str__(self) -> str:
        """Control the string representation of these records.

        Returns:
            str: the string representation of the record
        """
        return f"{self.name} | {self.url}"

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
            url=self.url,
            params=params,
            auth=self.AuthClass(self.credential_id, self.credential_secret),
        )

    @property
    def url(self) -> str:
        """Provide the URL for accessing the client.

        Returns:
            str: the URL, consisting of scheme, host, and path
        """
        return "/".join([str(self.host).rstrip("/"), str(self.path).lstrip("/")])


class PropertyAddress(TypedDict):
    """Document keys used to identify properties in the HouseCanary API."""

    #: House number and street, e.g. ``7500 Melrose Ave``
    address: str

    #: The 5-digit zipcode
    zipcode: str


class Property(Model):
    """Model property data retrieved from the HouseCanary API.

    This model is extensible and can be reused for additional APIs in the future. When
    integrating with future APIs:
        - generate a new Django app: canary_core.api_client
        - refactor this model to be stored in the new app
        - remove any HouseCanary API-specific fields
        - import the base model from the new app, and extend it here for HouseCanary
    """

    class Meta:
        """Specify the plural name."""

        verbose_name_plural = _("Properties")

    class SewageType(TextChoices):
        """Enumerate the sewage type choices retrieved from HouseCanary."""

        UNKNOWN = "UN", _("Unknown")
        NONE = "NO", _("None")
        MUNICIPAL = "MU", _("Municipal")
        STORM = "ST", _("Storm")
        SEPTIC = "SE", _("Septic")
        YES = "YS", _("Yes")

    apiclient: "ForeignKey[Property, BasicAPIClient]" = ForeignKey(
        to=BasicAPIClient,
        on_delete=SET_NULL,
        null=True,
        help_text=_("The API client provividing information for this property"),
    )
    owners: "ManyToManyField[Property, User]" = ManyToManyField(
        to=User,
        related_name="properties",
        swappable=True,
        help_text=_(
            "these users own the property or act on behalf of the property owner; they "
            "are authorized to access sensitive information about the property"
        ),
    )

    # TODO: migrate to using AddressField from `django-address` some day
    identifier = JSONField(
        default=dict,
        unique=True,
        help_text=_(
            "store address information as JSON for use with the HouseCanary API"
        ),
    )
    assessment_date: "DateField" = DateField(
        null=True, help_text=_("the date at which the property was assessed")
    )
    sewage_type: "CharField" = CharField(
        max_length=2, choices=SewageType.choices, default=SewageType.UNKNOWN
    )
    other_data = JSONField(default=dict, verbose_name=_("Other Data"))

    def __str__(self) -> str:
        """Define the record's string representation.

        Returns:
            str: the string representation of the record
        """
        return " | ".join(f"{k.title()} {v}" for k, v in dict(self.identifier).items())

    @classmethod
    def from_client(
        cls,
        api_client: BasicAPIClient,
        address: PropertyAddress,
        save: bool = False,
        **kwargs: Any,
    ) -> "Property":
        """Instantiate a new :class:`Property` from the given client + parameters.

        The query string parameters are used to identify the property to select.

        Args:
            api_client (BasicAPIClient): use this client to retrieve the data for this
                property
            address (PropertyAddress): this is directly stored in the ``identifier``
                field
            save (bool): save the record to the DB; defaults to ``False``
            **kwargs (Any): additional keyword arguments are passed directly to the
                :class:`Property` initializer

        Returns:
            Property: the new :class:`Property` record; will only be saved if the
                ``save`` argument is truth-y
        """
        prop = cls(apiclient=api_client, identifier=address, **kwargs)
        return prop.fetch_and_update(save=save)

    def fetch(self) -> Response:
        """Update this record with data retrieved from its API client.

        Ignore DAR402 b.c. `darglint` is unaware of exceptions raised by called
        methods.

        noqa: DAR402
        Raises:
            HttpError: raised by the API client for unsuccessful API requests

        Returns:
            Response: the :class:`Response` object from the HouseCanary API request
        """
        # pylint: disable=no-member     # it really does have the `get()` method
        resp = self.apiclient.get(**dict(self.identifier))
        resp.raise_for_status()
        return resp

    def fetch_and_update(self, save: bool = False) -> "Property":
        """Fetch data from the API client and update this record, optionally saving.

        Provided for convenience.

        Args:
            save (bool): if set, save the record after updating it; defaults to False

        Returns:
            Property: return ``self`` after applying changes
        """
        resp = self.fetch()
        self.update(resp.json())

        if save:
            self.save()

        return self

    def update(self, api_data: dict[str, Any]) -> "Property":
        """Update this object with the provided HouseCanary API data.

        # TODO: implement a more rigorous serializer for deserializing API data

        # NOTE: properties are updated, but the record is not saved

        Args:
            api_data (dict[str, Any]): the raw data from a request to the HouseCanary
                API

        Returns:
            Property: returns ``self`` for convenience
        """
        # pylint: disable=no-member     # it really does have the `.path` attr
        key = str(self.apiclient.path).strip("/")
        result = api_data.get(key, {}).get("result", {})

        try:
            sewage_type = str(result["property"].pop("sewer") or "Unknown").upper()
        except KeyError:
            logger.error(
                "failed to retrieve sewage type from response %s",
                api_data,
                exc_info=True,
            )
        else:
            try:
                self.sewage_type = self.SewageType[sewage_type]
            except KeyError:
                logger.error("unrecognized sewage type: %s", sewage_type, exc_info=True)

        try:
            assessment_year = result.get("assessment").pop("assessment_year")
        except KeyError:
            logger.error(
                "failed to retrieve assessment year from response %s",
                api_data,
                exc_info=True,
            )
        else:
            self.assessment_date = dt.date(year=assessment_year, month=1, day=1)

        if result:
            self.other_data = result

        return self


logger.debug("imported module %s", __name__)
