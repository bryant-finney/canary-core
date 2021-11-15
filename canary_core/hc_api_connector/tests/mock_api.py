"""Mock out the HouseCanary API for the client to use.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import base64
import json
import logging
from pathlib import Path

# django packages
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest, QueryDict
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.urls.conf import include, path, re_path
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

# third party
import pkg_resources as pr

# local
from canary_core.hc_api_connector.tests.mock_auth import GenericAPIAuthentication

logger = logging.getLogger(__name__)
User = get_user_model()


def encode_to_basename(params: QueryDict) -> str:
    """Encode the provided query string parameters to the basename of response file.

    Args:
        params (QueryDict): the query string parameters identifying the property
            to the HouseCanary API

    Returns:
        str: the encoded the given parameters encoded as a string
    """
    return base64.b64encode(params.urlencode().encode()).decode()


def house_canary(request: HttpRequest) -> HttpResponse:
    """Mock the HouseCanary API by providing a pre-loaded response.

    Args:
        request (HttpRequest): the incoming request object after passing through all
            middleware layers

    Returns:
        HttpResponse: a representative response similar to the HouseCanary API
    """
    if not request.GET:
        return HttpResponseBadRequest(
            content=_("query string parameters required to identify property")
        )
    basename = encode_to_basename(request.GET)
    fname = Path(pr.resource_filename(__name__, f"{basename}.json"))

    try:
        with open(fname, "rb") as f:
            resp_data = f.read()
    except FileNotFoundError:
        return HttpResponseNotFound(
            content=json.dumps({"msg": "no such property", "detail": request.GET}),
            content_type="application/json",
        )

    return HttpResponse(content=resp_data, content_type="application/json")


class UserSerializer(ModelSerializer):
    """Define a dummy serializer for use in tests."""

    class Meta:
        """Set the model and fields."""

        model = User
        fields = "__all__"


class UserViewSet(ModelViewSet):
    """Define a dummy viewset for use in tests.

    This viewset mocks the HouseCanary API.
    """

    name = "users"
    authentication_classes = [GenericAPIAuthentication]
    filterset_fields = UserSerializer.Meta.fields
    ordering_fields = UserSerializer.Meta.fields
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


router = DefaultRouter()
router.register(r"users", UserViewSet)
urlpatterns = [
    re_path(r"^api/", include((router.urls, "mock_api"), namespace="mock_api")),
    path("property/details/", house_canary),
]
