# autovm

A virtual machine management system

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


- [autovm](#autovm)
  - [Settings](#settings)
  - [Basic Commands](#basic-commands)
    - [Running a local instance](#running-a-local-instance)
    - [Email Server](#email-server)
    - [Setting Up Users](#setting-up-users)
      - [Running tests with pytest](#running-tests-with-pytest)
    - [Test coverage](#test-coverage)
    - [Sentry](#sentry)
  - [Deployment](#deployment)

## Settings



## Basic Commands

### Running a local instance

```bash
docker compose -f docker-compose.local.yml up
```

Access the administrative dashboard on `http://127.0.0.1:8000/admin`.

**For this setup , administrative credentials have been provided as below:**
> [!NOTE]
> For this setup , administrative credentials have been provided as below:

Email:

Password:


### Email Server

To test email notifications sent to users  local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container at `http://127.0.0.1:8025`

### Setting Up Users

- To create a **superuser account**, use this command:

      $ docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser


#### Running tests with pytest

    $ pytest


### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

### Sentry


## Deployment
