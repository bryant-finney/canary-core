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
