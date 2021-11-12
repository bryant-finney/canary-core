"""Model data from the HouseCanary API.

.. moduleauthor:: Bryant Finney
   :github: https://bryant-finney.github.io/about
"""
# stdlib
from typing import Type

# django packages
from django.contrib.auth import get_user_model
from django.db.models import Model

User: Type[Model] = get_user_model()
