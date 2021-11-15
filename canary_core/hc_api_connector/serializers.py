"""Define serializers for database models.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import logging

# django packages
from rest_framework.serializers import ModelSerializer

# local
from canary_core.hc_api_connector.models import BasicAPIClient, Property

logger = logging.getLogger(__name__)


class BasicAPIClientSerializer(ModelSerializer):
    """Define a serializer for the :class:`BasicAPIClient` model."""

    class Meta:
        """Set the model and fields to serialize."""

        model = BasicAPIClient
        fields = "__all__"


class PropertySerializer(ModelSerializer):
    """Define a serializer for the :class:`Property` model."""

    class Meta:
        """Set the model and fields to serialize."""

        model = Property
        fields = "__all__"
        filterset_fields = ["assessment_date", "sewage_type", "owners"]


logger.debug("imported module %s", __name__)
