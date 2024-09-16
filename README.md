# virtualmachinemanager_server

A virtual machine management platform with automation, role-based access control (RBAC), and seamless payment integration.

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


- [virtualmachinemanager\_server](#virtualmachinemanager_server)
    - [Running a local instance](#running-a-local-instance)
  - [Setting up your initial data](#setting-up-your-initial-data)
    - [Admin dashboard](#admin-dashboard)
  - [Accessing the email server](#accessing-the-email-server)
  - [Background tasks](#background-tasks)
  - [Running tests with pytest](#running-tests-with-pytest)



### Running a local instance

```bash
docker compose -f docker-compose.local.yml build
docker compose -f docker-compose.local.yml up
```

## Setting up your initial data


You can also create the initial data for the project via:
```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py initializedata
```

The above populates all relevant tables with three customers and administrators.
Each user can authenticate with the following format

> [!NOTE]
> **username:** customer1@mail.com ... customer3@mail.com **OR** admin1@mail.com ... admin3@mail.com
>
> **password**: password
>
**Example**

To access customer2's account:

```bash
EMAIL=customer2@mail.com

PASSWORD=password
```
### Admin dashboard
You can run your migrations or commands against the project with commands in the following format
```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py createadmin
```


The above creates an administrator with credentials as provided from your environment. For this you can use `vmadmin@virtualmachinemanager.com` and `vmadminpassword`respectively

```bash
EMAIL=vmadmin@virtualmachinemanager.com

PASSWORD=vmadminpassword
```

Access the administrative dashboard on `http://127.0.0.1:8000/admin`.

API Documentation `http://127.0.0.1:8000/api/docs`


Alternatively, if you want the traditional way:

- To create a **superuser account**, use this command:

      $ docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
## Accessing the email server

To test email notifications sent to users local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container at `http://127.0.0.1:8025`

## Background tasks
Background tasks handle notifications such as:

- Sharing the transfer of virtual machines between users.
- Activation and deactivation of an account by an administrator

You can view the status of these on the following URL: http://localhost:5555 with credentials from the envs.local.django file path

## Running tests with pytest

    $ docker compose -f docker-compose.local.yml run django pytest
