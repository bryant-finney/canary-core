"""Perform tests on the BasicAPIClient model.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
from typing import Iterator

# django packages
from django.test.client import Client

# third party
import pytest
from pytest_django.fixtures import SettingsWrapper

# local
from canary_core.hc_api_connector.models import BasicAPIClient

CREDENTIAL_ID = f"test-cred-id-{__name__}"
CREDENTIAL_SECRET = f"test-cred-secret-{__name__}"

pytestmark = pytest.mark.django_db


@pytest.fixture
def enable_auth_class(settings: SettingsWrapper) -> None:
    """Enable the mock API's auth class.

    Args:
        settings (SettingsWrapper): use this fixture to append the auth class to the
            setting in ``REST_FRAMEWORK``
    """
    auth_class = "canary_core.hc_api_connector.tests.mock_auth.GenericAPIAuthentication"
    if auth_class not in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
        settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(auth_class)


@pytest.fixture
def basic_api_client() -> Iterator[BasicAPIClient]:
    """Get or create a :class:`BasicAPIClient` object.

    After the test, delete it.

    Yields:
        BasicAPIClient: the test record
    """
    client, _ = BasicAPIClient.objects.get_or_create(
        credential_id=CREDENTIAL_ID, credential_secret=CREDENTIAL_SECRET
    )
    try:
        yield client
    finally:
        client.delete()


@pytest.mark.usefixtures("enable_auth_class")
@pytest.mark.urls("canary_core.hc_api_connector.tests.mock_api")
def test_authenticate(client: Client, basic_api_client: BasicAPIClient) -> None:
    """Verify that the credentials can retrieve mock user records."""  # noqa:DAR101
    resp = client.get("/api/users/", **basic_api_client.auth_header)
    assert resp.status_code == 200
