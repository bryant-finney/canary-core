"""Mock out the HouseCanary API for the client to use.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import logging

# django packages
from django.contrib.auth import get_user_model
from django.urls.conf import include, re_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

# local
from canary_core.hc_api_connector.tests.mock_auth import GenericAPIAuthentication

logger = logging.getLogger(__name__)
User = get_user_model()


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
    re_path(r"^api/", include((router.urls, "mock_api"), namespace="mock_api"))
]
