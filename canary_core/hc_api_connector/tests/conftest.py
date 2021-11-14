"""Configure settings for the tests in the package.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
from __future__ import annotations

# stdlib
import json
import logging
from base64 import b64decode
from pathlib import Path
from typing import Any, Iterator

# django packages
from django.http.request import QueryDict
from django.utils.http import urlencode, urlunquote_plus

# third party
import pkg_resources as pr
import pytest
from pytest_django.fixtures import SettingsWrapper
from pytest_django.live_server_helper import LiveServer

# local
from canary_core.hc_api_connector.models import BasicAPIClient
from canary_core.hc_api_connector.tests.mock_api import encode_to_basename

# pylint: disable=unused-argument,redefined-outer-name

CREDENTIAL_ID = f"test-cred-id-{__name__}"
CREDENTIAL_SECRET = f"test-cred-secret-{__name__}"

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


@pytest.fixture
def root_urlconf(settings: SettingsWrapper) -> SettingsWrapper:
    """Override the ``ROOT_URLCONF`` setting for the tests that use this fixture.

    The ROOT_URLCONF settings instead points at the mock_api module in this package.

    Args:
        settings (SettingsWrapper): depend on this fixture for applying the override

    Returns:
        SettingsWrapper: the settings object
    """
    settings.ROOT_URLCONF = __name__.rsplit(".", maxsplit=1)[0] + ".mock_api"
    return settings


@pytest.fixture
def enable_auth_class(settings: SettingsWrapper) -> SettingsWrapper:
    """Enable the mock API's auth class.

    Args:
        settings (SettingsWrapper): use this fixture to append the auth class to the
            setting in ``REST_FRAMEWORK``

    Returns:
        SettingsWrapper: the updated ``settings`` object
    """
    auth_class = "canary_core.hc_api_connector.tests.mock_auth.GenericAPIAuthentication"
    if auth_class not in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
        settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(auth_class)
    return settings


@pytest.fixture
def mock_api_client(
    root_urlconf: SettingsWrapper,
    enable_auth_class: SettingsWrapper,
    live_server: LiveServer,
) -> Iterator[BasicAPIClient]:
    """Get or create a :class:`BasicAPIClient` object.

    After the test, delete it.

    Args:
        root_urlconf (SettingsWrapper): depend on this fixture to enable the mock API
        enable_auth_class (SettingsWrapper): depend on this fixture to enable the auth
            class used by the mock API server
        live_server (LiveServer): configure the API client to reference the mock
            server's host and path

    Yields:
        BasicAPIClient: the test record
    """
    # BasicAPIClient really does have an `objects` property
    client, _ = BasicAPIClient.objects.get_or_create(  # pylint: disable=no-member
        credential_id=CREDENTIAL_ID,
        defaults=dict(
            credential_secret=CREDENTIAL_SECRET,
            host=live_server.url,
            path="/property/details/",
        ),
    )
    try:
        yield client
    finally:
        client.delete()


@pytest.fixture
def query_params() -> dict[str, str]:
    """Decode the filename to get the correct query params to GET it.

    Returns:
        dict[str, str]: the query string parameters that were encoded when naming the
            mock API's response file
    """
    dirname = Path(pr.resource_filename(__name__.rsplit(".", maxsplit=1)[0], ""))
    fname = next(dirname.glob("*.json"))

    params: dict[str, str] = dict(
        tuple(param.split("=", maxsplit=1))  # type: ignore  # mypy unaware of maxsplit
        for param in urlunquote_plus(b64decode(fname.stem).decode()).split("&")
    )

    return params


@pytest.fixture
def mock_api_response_data(query_params: dict[str, str]) -> dict[str, Any]:
    """Load the mock API's response data for comparison during tests.

    Args:
        query_params (dict[str, str]): depend on this fixture of the query string
            parameters to encode

    Returns:
        dict[str, Any]: the mock API's response data to the given `query_params`
    """
    basename = encode_to_basename(QueryDict(urlencode(query_params)))
    fname = Path(pr.resource_filename(__name__, f"{basename}.json"))

    with open(fname, "r", encoding="utf-8") as f:
        return json.load(f)
