# `canary_core`

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/bryant-finney/canary-core)

[![pipeline status](https://gitlab.com/django-canary/core/badges/main/pipeline.svg)](https://gitlab.com/django-canary/core/-/pipelines)
![coverage](https://gitlab.com/django-canary/core/badges/main/coverage.svg)
[![code style: black](https://user-content.gitlab-static.net/e7b1487736a40a602d6d6861a3e0d4f95392e460/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f636f64652532307374796c652d626c61636b2d3030303030302e737667)](https://github.com/psf/black)
[![pre-commit: enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![repo: gitlab](https://img.shields.io/badge/repo-gitlab-violet)](https://gitlab.com/django-canary/core)

Define the `canary_core` Django project for interfacing with the HouseCanary API. This
project provides a custom Django app for interacting with third-party APIs providing
property data: [`canary_core.hc_api_connector`](canary_core/hc_api_connector/apps.py)

## System Dependencies

Two development strategies are supported by this project: container-based development
using Docker, or bare-metal development from a virtual environment. The former requires
minimal system dependencies; however, it requires additional IDE configuration steps
for PyCharm and VSCode, which are not covered here.

When developing from a virtual environment, the following system dependencies are
recommended:

- [`docker`](https://docs.docker.com/desktop/mac/install/)
  - alternatively, all optional dependencies (except `direnv` and `tox`) must be
    installed to support this application
- [`docker-compose`](https://docs.docker.com/compose/install/)
  - Docker Desktop for `macOS` and `Windows` provide the Docker Compose CLI; this may
    be used instead
- (optional) [`poetry`](https://python-poetry.org/docs/#installation)
  - only required when working from a virtual environment; VSCode can be used to
    develop directly from inside the project's Docker container
- (optional) [`direnv`](https://direnv.net/docs/installation.html)
  - this provides a shortcut to setup/update the project's dev environment; an
    alternative is to just run the following:
    ```bash
    $ . ./.envrc
    ```
- (optional) [`postgresql 14`](https://formulae.brew.sh/formula/postgresql)
  - the [db image](./db/Dockerfile) managed by this project may be used instead
- (optional) [`tox`](https://tox.wiki/en/latest/install.html)
  - `tox` is used to run the test suite using multiple `python` interpreter versions;
    it works best with [`pyenv`](https://github.com/pyenv/pyenv#installation)

## Production Setup

This project manages Docker images for its API and database layers; accordingly,
multiple frameworks can be used to orchestrate the containers.

Demo on a single system:

1. Download [`docker-compose.yml`](./docker-compose.yml) and [`base.env`](./base.env)
2. Rename `base.env` ⇨ `.env`
3. Launch the app by calling `docker-compose up`
4. Navigate to [localhost:8000](http://localhost:8000/) to use the app

## Development Setup

After selecting a development strategy and installing necessary dependencies, see the
following steps for completing the environment setup.

### Container-based Development

To start the minimal production containers locally, you can use `docker-compose`.

1. Clone this repo
2. `. ./.envrc` to set environment variables
3. `docker-compose pull` to pull the required Docker images
4. `export CANARY_CORE_CMD='django-admin runserver'` in order to run the development
   server (by default, the API container runs `sleep infinity`)
5. To create the shortcut `dev-compose`, run `eval "$(CANARY_ALIASES)"`
   - this is just an alias for `docker-compose -f docker-compose.yml -f compose/dev.yml`
6. Finally, run `dev-compose up -d`

The above should start a network of three containers: `db` (the `postgresql` database),
`house_canary` (the HouseCanary mock API server), and `api` (the core API container).

### Virtual Environment

To perform the environment setup:

1. Clone this repo
2. `direnv allow` to allow `direnv` to automatically execute [.envrc](.envrc)
3. Run `./api/docker-entrypoint.sh` to start the development server
4. To start the mock HouseCanary API server, run the following:
   ```zsh
   $ CANARY_CORE_ROOT_URLCONF=canary_core.hc_api_connector.tests.mock_api django-admin runserver localhost:8080
   ```

## Next Steps

- [ ] integrate authorization class / model for restricting property data access to
      property owners + staff
- [ ] split `pre-commit` QA jobs into `mypy`, `flake8`, `black`, and `prettier` for
      more clarity/better feedback
- [ ] add routes for integrating [`drf-yasg`](https://github.com/axnsan12/drf-yasg) to
      document the API
- [ ] build and publish package to internal registry using a CI job
- [ ] add integration tests for the primary application

---

# Appendix

The following was generated by GitLab and is retained as a reference.

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/django-canary/core.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/integrations/)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Automatically merge when pipeline succeeds](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://docs.gitlab.com/ee/user/clusters/agent/)

---

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thank you to [makeareadme.com](https://gitlab.com/-/experiment/new_project_readme_content:513816de6d7902a812b50d4958b76a62?https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name

Choose a self-explaining name for your project.

## Description

Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges

On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals

Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support

Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap

If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing

State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment

Show your appreciation to those who have contributed to the project.

## License

For open source projects, say how it is licensed.

## Project status

If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
