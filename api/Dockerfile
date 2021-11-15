# -------------------------------------------------------------------------------------
# Summary: Define a minimal Docker image for the API layer of the stack.
# Created: 2021-11-10 20:06:11
# Author:  Bryant Finney (https://bryant-finney.github.io/about)
# Note:    This image is built using BuildKit features
#            https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds
# -------------------------------------------------------------------------------------
FROM python:3.10-alpine AS base

COPY ./api/install_alpine_deps.sh /usr/local/bin/install-deps

RUN install-deps

# match the default clone directory for GitLab's Docker executor
WORKDIR /builds/django-canary/core

ENV \
  DJANGO_SETTINGS_MODULE=canary_core.settings                                     \
  PIP_NO_CACHE_DIR="off"                                                          \
  POETRY_VIRTUALENVS_CREATE=false                                                 \
  POETRY_HOME="/opt/poetry"
EXPOSE 8000

RUN pip install poetry

# this script is made executable in the next RUN directive
COPY ./api/docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]

FROM base AS minimal-deps

COPY ./pyproject.toml ./poetry.lock ./
RUN echo "installing minimal dependencies with poetry" \
  && poetry install --no-interaction --no-root --no-dev ; chmod +x /docker-entrypoint.sh

FROM minimal-deps AS dev

RUN install-deps --extras

# use a separate layer for `dev` dependencies to support caching
RUN echo "installing dev dependencies with poetry" \
  # the following line reinstalls virtualenv + msgpack, which have been removed by the
  # previous `poetry install` command
  && pip install poetry \
  && poetry install --no-interaction --no-root

COPY . .
RUN echo "installing package in development mode" \
  && poetry install --no-interaction

CMD ["django-admin", "runserver", "0.0.0.0:8000"]

FROM dev AS pkg-build

RUN echo "build wheel" && poetry build -f wheel

FROM minimal-deps AS prod

WORKDIR /work
COPY --from=pkg-build /builds/django-canary/core/dist/*.whl ./

RUN echo "installing wheel" && pip install *.whl
CMD [ "/usr/local/bin/gunicorn", "canary_core.wsgi:application", "--bind 0.0.0.0:8000"]
