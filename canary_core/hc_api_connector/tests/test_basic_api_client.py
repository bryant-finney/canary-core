"""Perform tests on the BasicAPIClient model.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
from typing import TYPE_CHECKING, Iterator

# django packages
from django.contrib.auth import get_user_model
from django.test.client import Client

# third party
import pytest
from pytest_django.live_server_helper import LiveServer

# local
from canary_core.hc_api_connector.models import BasicAPIClient
from canary_core.hc_api_connector.tests.mock_api import UserSerializer

CREDENTIAL_ID = f"test-cred-id-{__name__}"
CREDENTIAL_SECRET = f"test-cred-secret-{__name__}"

if TYPE_CHECKING:
    # django packages
    from django.contrib.auth.models import User  # noqa: I005  # pragma: no cover
else:
    User = get_user_model()


@pytest.fixture
def basic_api_client(live_server: LiveServer) -> Iterator[BasicAPIClient]:
    """Get or create a :class:`BasicAPIClient` object.

    After the test, delete it.

    Args:
        live_server (LiveServer): configure the API client to reference the mock
            server's host and path

    Yields:
        BasicAPIClient: the test record
    """
    client, _ = BasicAPIClient.objects.get_or_create(
        credential_id=CREDENTIAL_ID,
        defaults=dict(
            credential_secret=CREDENTIAL_SECRET, host=live_server.url, path="/api/users"
        ),
    )
    try:
        yield client
    finally:
        client.delete()


@pytest.fixture
def user() -> Iterator[User]:
    """Get or create a test user record.

    After the test, delete it.

    Yields:
        User: a user record
    """
    user, _ = User.objects.get_or_create(
        username="test.user",
        defaults=dict(
            email="test.user@junk.com",
            first_name="Test",
            last_name="User",
            password="dummy",
            is_active=True,
        ),
    )
    try:
        yield user
    finally:
        user.delete()


@pytest.mark.usefixtures("enable_auth_class")
@pytest.mark.urls("canary_core.hc_api_connector.tests.mock_api")
def test_authenticate(client: Client, basic_api_client: BasicAPIClient) -> None:
    """Verify that the credentials can retrieve mock user records."""
    # NOTE: `mypy` unable to distinguish the used kwargs and expects `bool` values
    resp = client.get("/api/users/", **basic_api_client.auth_header)  # type: ignore
    assert resp.status_code == 200


@pytest.mark.usefixtures("enable_auth_class")
@pytest.mark.urls("canary_core.hc_api_connector.tests.mock_api")
def test_get_request(user: User, basic_api_client: BasicAPIClient) -> None:
    """Verify functionality of `BasicAPIClient.get()`."""
    resp = basic_api_client.get()
    resp.raise_for_status()

    response_data = resp.json()["results"]
    user_data = UserSerializer(instance=[user], many=True).data

    assert user_data == response_data


def test_client_string_repr(basic_api_client: BasicAPIClient) -> None:
    """Verify string formatting for the basic API client model."""
    client_str = str(basic_api_client)

    assert basic_api_client.name in client_str
    assert basic_api_client.url in client_str
