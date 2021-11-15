"""Test functionality of the primary API endpoint.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import json

# django packages
from django.test import RequestFactory

# local
from canary_core.hc_api_connector.models import BasicAPIClient, PropertyAddress
from canary_core.hc_api_connector.views import has_septic


def test_nominal_has_septic(
    rf: RequestFactory, mock_api_client: BasicAPIClient, query_params: PropertyAddress
) -> None:
    """Verify nominal behavior of the `has_septic` endpoint."""
    request = rf.get("/", data=query_params)

    response = has_septic(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {"septic": False}
