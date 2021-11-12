"""Configure app settings.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# django packages
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HCAPIConnectorConfig(AppConfig):
    """Define the ``AppConfig`` class + settings for the ``hc_api_connector`` app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "canary_core.hc_api_connector"
    verbose_name = _("HouseCanary API Connector")
