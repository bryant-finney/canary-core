"""Validate the mock API for HouseCanary.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# local
from canary_core.hc_api_connector.models import BasicAPIClient


def test_mock_api_client(
    mock_api_client: BasicAPIClient, query_params: dict[str, str]
) -> None:
    """Verify the ``mock_api_client``."""
    resp = mock_api_client.get(**query_params)
    resp.raise_for_status()
    resp_data = resp.json()

    assert "property/details" in resp_data
    assert "result" in resp_data["property/details"]
    assert "property" in resp_data["property/details"]["result"]
    assert "assessment" in resp_data["property/details"]["result"]
