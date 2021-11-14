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
        defaults={
            **dict(
                identifier=query_params,
            ),
            **PROPERTY_DEFAULTS,
        },
        apiclient=mock_api_client,
    )

    try:
        yield prop
    finally:
        prop.delete()


def test_property_fetch(property_record: Property) -> None:
    """Verify :func:`Property.fetch()`."""
    resp = property_record.fetch()
    full_resp_data = resp.json()

    # perform some assertions about the response structure
    assert str(property_record.apiclient.path).strip("/") in full_resp_data

    resp_data = full_resp_data[str(property_record.apiclient.path).strip("/")]

    assert "result" in resp_data
    assert "property" in resp_data["result"]
    assert "assessment" in resp_data["result"]


def compare_dicts(d1: dict[Any, Any], d2: dict[Any, Any]) -> None:
    """Recursively assert equality for both dictionaries.

    Args:
        d1 (dict[Any, Any]): the first dictionary to compare
        d2 (dict[Any, Any]): the second
    """
    assert sorted(d1.keys()) == sorted(d2.keys())
    for k, v in d1.items():
        if hasattr(v, "items"):
            compare_dicts(v, d2[k])
            continue
        assert v == d2[k]


def test_property_fetch_data(
    property_record: Property, mock_api_response_data: dict[str, Any]
) -> None:
    """Verify the response data of :func:`Property.fetch()` from the mock API."""
    resp_data = property_record.fetch().json()
    compare_dicts(resp_data, mock_api_response_data)


def test_property_update(
    property_record: Property, mock_api_response_data: dict[str, Any]
) -> None:
    """Verify :func:`Property.update()`."""
    # confirm the initial state of the Property record
    assert all(getattr(property_record, k) == v for k, v in PROPERTY_DEFAULTS.items())

    property_record.update(mock_api_response_data)

    # confirm all properties have changed
    assert all(getattr(property_record, k) != v for k, v in PROPERTY_DEFAULTS.items())

    # ensure the record can be saved
    property_record.save()
