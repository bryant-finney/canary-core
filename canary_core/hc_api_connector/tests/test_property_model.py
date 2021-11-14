"""Provide tests for the :class:`Property` model.

.. moduleauthor:: Bryant Finney <finneybp@gmail.com>
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
from typing import Any, Iterator

# third party
import pytest

# local
from canary_core.hc_api_connector.models import BasicAPIClient, Property

PROPERTY_DEFAULTS: dict[str, Any] = dict(
    assessment_date=None, sewage_type=Property.SewageType.UNKNOWN, other_data={}
)


@pytest.fixture
def property_record(
    mock_api_client: BasicAPIClient, query_params: dict[str, str]
) -> Iterator[Property]:
    """Create a :class:`Property` record for use in tests.

    The property record relates to the ``mock_api_client`` fixture; it is deleted after
    the test completes.

    Args:
        mock_api_client (BasicAPIClient): link the :class:`Property` record to the
            mock API client record
        query_params (dict[str, str]): use the query parameters dictionary as the
            property's identifier

    Yields:
        Property: the property record for use in tests; it is deleted after the tests
    """
    prop, _ = Property.objects.get_or_create(
        defaults=dict(
            identifier=query_params,
        )
        | PROPERTY_DEFAULTS,
        apiclient=mock_api_client,
    )

    try:
        yield prop
    finally:
        prop.delete()


def test_property_fetch(property_record: Property) -> None:
    """Verify :func:`Property.fetch()`."""
    # confirm the initial state of the Property record
    assert all(getattr(property_record, k) == v for k, v in PROPERTY_DEFAULTS.items())

    resp = property_record.fetch()
    full_resp_data = resp.json()

    # perform some assertions about the response structure
    assert str(property_record.apiclient.path).strip("/") in full_resp_data

    resp_data = full_resp_data[str(property_record.apiclient.path).strip("/")]

    assert "result" in resp_data
    assert "property" in resp_data["result"]
    assert "assessment" in resp_data["result"]
