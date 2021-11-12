"""Registry models with the `admin` application.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
import inspect

# django packages
from django.contrib import admin
from django.db.models import Model

# local
from canary_core.hc_api_connector import models

for cls in (
    v
    for k, v in models.__dict__.items()
    if not k.startswith("__") and inspect.isclass(v)
):
    if issubclass(cls, Model) and cls.__module__ == models.__name__:
        admin.site.register(cls)
