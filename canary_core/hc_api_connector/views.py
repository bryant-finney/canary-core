"""Define views and viewsets for this app's restful api.

.. moduleauthor:: bryant finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import json
import logging

# django packages
from django.http.request import HttpRequest
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

# third party
from requests import HTTPError
from requests.exceptions import ConnectionError

# local
from canary_core.hc_api_connector.models import BasicAPIClient, Property
from canary_core.hc_api_connector.serializers import (
    BasicAPIClientSerializer,
    PropertySerializer,
)

# NOTE: pylint was struggling with the Django Model classes
# pylint: disable=no-member

logger = logging.getLogger(__name__)


class BasicAPIClientViewSet(ModelViewSet):  # pylint: disable=too-many-ancestors
    """Provide a view set for interacting with `BasicAPIClient` records."""

    name = "apiclients"
    filterset_fields = BasicAPIClientSerializer.Meta.fields
    ordering_fields = BasicAPIClientSerializer.Meta.fields
    permission_classes = [IsAuthenticated]
    queryset = BasicAPIClient.objects.all()
    serializer_class = BasicAPIClientSerializer


class PropertyViewSet(ModelViewSet):  # pylint: disable=too-many-ancestors
    """Provide a view set for interacting with `Property` records."""

    name = "properties"
    filterset_fields = PropertySerializer.Meta.filterset_fields
    ordering_fields = PropertySerializer.Meta.fields
    permission_classes = [IsAuthenticated]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


def has_septic(request: HttpRequest) -> HttpResponse:
    """Check if the property at the given address uses a septic system.

    If the specified address isn't already tracked in the DB, use the first API client
    retrieved from the DB to create a new property record, querying the HouseCanary API
    to provide its initial data.

    # TODO: use a serializer for the query string parameters

    Args:
        request (HttpRequest): the incoming `GET` request

    Returns:
        HttpResponse: on success, the response body contains `{"septic": bool}`
    """
    address = request.GET.dict()
    try:
        prop: Property = Property.objects.get(identifier=address)
    except Property.DoesNotExist:
        api_client = BasicAPIClient.objects.first()
        if not api_client:
            return HttpResponseServerError(
                content_type="application/json",
                content=json.dumps({"msg": "Misconfigured: no API client records"}),
            )

        try:
            prop = Property.from_client(
                api_client,
                address,  # type: ignore
                save=True,
            )
        except HTTPError as e:
            return HttpResponse(
                status=e.response.status_code,
                content_type="application/json",
                content=e.response.content.decode(),
            )
        except ConnectionError as e:
            return HttpResponseServerError(
                content_type="application/json",
                content=json.dumps(
                    {"msg": "failed to connect to API", "detail": str(e)}
                ),
            )

    if prop.sewage_type in [None, prop.SewageType.UNKNOWN.value]:
        serializer = PropertySerializer(instance=prop)
        return HttpResponseBadRequest(
            content_type="application/json",
            content=json.dumps(
                {"msg": "unknown sewage type for property", "detail": serializer.data}
            ),
        )

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(
            {"septic": prop.sewage_type == prop.SewageType.SEPTIC.value}
        ),
    )


logger.debug("imported module %s", __name__)
