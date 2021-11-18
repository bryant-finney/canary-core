#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
# stdlib
import os
import sys


def main() -> None:
    """Run administrative tasks.

    Raises:
        ImportError: [description]
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canary_core.settings")
    try:
        # django packages
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
