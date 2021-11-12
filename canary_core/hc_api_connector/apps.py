"""Configure app settings.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# django packages
from django.apps import AppConfig


class HCAPIConnectorConfig(AppConfig):
    """Define the ``AppConfig`` class + settings for the ``hc_api_connector`` app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "canary_core.hc_api_connector"
