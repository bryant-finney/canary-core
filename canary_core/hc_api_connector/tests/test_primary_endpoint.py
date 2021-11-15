"""Test functionality of the primary API endpoint.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import json

# django packages
from django.test import RequestFactory

# third party
import pytest

# local
from canary_core.hc_api_connector.models import (
    BasicAPIClient,
    Property,
    PropertyAddress,
)
from canary_core.hc_api_connector.views import has_septic


def test_nominal_has_septic(
    rf: RequestFactory, mock_api_client: BasicAPIClient, query_params: PropertyAddress
) -> None:
    """Verify nominal behavior of the `has_septic` endpoint."""
    request = rf.get("/", data=query_params)

    response = has_septic(request)

    assert response.status_code == 200
    assert json.loads(response.content) == {"septic": False}


@pytest.mark.django_db
def test_house_canary_api_error(
    rf: RequestFactory, query_params: PropertyAddress, api_client: BasicAPIClient
) -> None:
    """Verify HouseCanary API connection errors are handled correctly."""
    request = rf.get("/", data=query_params)
    response = has_septic(request)

    assert response.status_code >= 500

    resp_data = json.loads(response.content)
    assert "msg" in resp_data
    assert "detail" in resp_data

    assert resp_data["msg"] == "failed to connect to API"


@pytest.mark.django_db
def test_house_canary_no_api_client_record(
    rf: RequestFactory, query_params: PropertyAddress
) -> None:
    """Verify the endpoint handles missing API client records for new properties."""
    request = rf.get("/", data=query_params)
    response = has_septic(request)

    assert response.status_code >= 500

    resp_data = json.loads(response.content)
    assert resp_data["msg"] == "Misconfigured: no API client records"


def test_property_not_found(
    rf: RequestFactory, mock_api_client: BasicAPIClient
) -> None:
    """Verify behavior when the requested address is not found."""
    fake_address = {"address": "not a real address"}
    request = rf.get("/", data=fake_address)

    response = has_septic(request)

    assert response.status_code == 404

    resp_data = json.loads(response.content)
    assert "msg" in resp_data
    assert "detail" in resp_data

    assert resp_data["msg"] == "no such property"
    assert resp_data["detail"] == fake_address


def test_unknown_sewage_type(
    rf: RequestFactory, mock_api_client: BasicAPIClient, query_params: PropertyAddress
) -> None:
    """Verify nominal behavior of the `has_septic` endpoint."""
    request = rf.get("/", data=query_params)
    prop: Property = Property.from_client(mock_api_client, query_params)
    prop.sewage_type = prop.SewageType.UNKNOWN.value
    prop.save()

    response = has_septic(request)

    assert response.status_code == 400

    resp_data = json.loads(response.content)
    assert "msg" in resp_data
    assert "detail" in resp_data

    assert resp_data["msg"] == "unknown sewage type for property"
