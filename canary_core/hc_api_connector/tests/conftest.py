"""Configure settings for the tests in the package.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import logging

# third party
import pytest
from pytest_django.fixtures import SettingsWrapper

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
def enable_auth_class(settings: SettingsWrapper) -> None:
    """Enable the mock API's auth class.

    Args:
        settings (SettingsWrapper): use this fixture to append the auth class to the
            setting in ``REST_FRAMEWORK``
    """
    auth_class = "canary_core.hc_api_connector.tests.mock_auth.GenericAPIAuthentication"
    if auth_class not in settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]:
        settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(auth_class)
