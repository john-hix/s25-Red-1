Team Red - Spring 2025

# Members

  - ryzenpay - Kobe Franssen - kfran027@odu.edu
  - john-hix - John Hicks - jhick046@odu.edu
  - freddiefred25 - Freddie Boateng - fboat001@odu.edu
  - abaus002 - Andrew Bausas - abaus002@odu.edu
  - dpate021 - Diya Patel - dpate021@odu.edu
  - z-targz - Chase Wallace - cwall043@odu.edu
  - paragonsean - Sean Baker - sbake021@odu.edu


# Dev environment

Required software:

- Python 3.12
  - Should be available via OS package manager
- Make
  - Should be available via OS package manager
- Common UNIX utilities: `rm`, `find`, `test`, etc. used in Makefile.
- Visual Studio Code
  - [Download](https://code.visualstudio.com/download)
- Docker Engine (not `docker-compose` standalone program)
  - Docs: [install docker engine](https://docs.docker.com/engine/install/)

# VSCode setup

Install extensions:

- ms-python.black-formatter
- ms-python.isort
- ms-python.debugpy
- ms-python.python
- ms-python.pylint
- ms-python.mypy-type-checker
- ms-azuretools.vscode-docker

Complete steps under "Python environment" before continuing.
(VSCode will have errors when opening Python
files until you complete the steps under the "Python environment" heading.)


With the Python environment setup complete, open VSCode as a workspace
in the CudeCode project directory. 

# Make

We use Make to create an easy entry point for running commands in both
local development and CI/CD environments. Once a developer gets acclimated
to the project, it is likey that the Makefile will not support all needed use-cases;
the developer will end up needing to invoke some commands directly, not using
the make commands provided. See the `Makefile` contents for a examples of
cli program invocations and links to related documentation.

## Setup

Install make using your OS's method.

Ubuntu: `sudo apt update && sudo apt install make -y`

# Docker for service dependencies

The project uses Docker Compose to manage application service-level dependencies,
such as the Postgres database.

The Makefile provides several convenience commands for the developer to use.

- `make docker-run` will bring up the Docker Compose stack, building volumes and
  networks as necessary.
- `make docker-down` will bring down the Docker Compose stack, while also
  retaining data that was written to Docker volumes during execution. This allows
  data to persist between development sessions.
- `make docker-clean` will bring down the Docker compose stack AND remove ALL DATA
  by deleting the Docker volumes associated with this project.

More information on Docker:
- [Compose](https://docs.docker.com/compose/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)

NOTE: the `docker-compose.yml` file intentionally publishes its services only
on the `localhost` network interface, to avoid opening the developer's machine
to remote attacks.

## PGAdmin

PG Admin is a GUI that can be helpful during database development.

When using PG Admin, log in at `http://localhost:2345`, using `admin@example.com`
for the user and `password` for the password.

To connect to the Postgres database, follow the instructions below.

1. On the right-hand side, right-click the "Servers" menu option.
2. Drill down: Register -> Server...
3. In the dialog that appears, enter "dev" as the name.
3. Click the "Connection" tab.
4. Enter the following information:
    - Host name/address: `postgres`
    - Port: `5432`
    - Maintenance database: `postgres`
    - Password: `password`
    - Save password?: Yes
5. Click "Save"
6. It should have connected successfully.

# Python environment setup

With Python installed on your system, complete the following:

1. Create a .venv folder: `make venv`
2. Open VSCode and confirm that VSCode errors to do not appear when you open
  Python files.
3. Try editing a Python file and saving to test the `black` and `isort`
  integration for formatting files.

## Troubleshooting: Set VSCode Python interpreter

If you have problems with "connecting to server"
for Python files, you can use the manual steps below to set the Python interpreter
for your VSCode workspace.

Select the Python interpreter within `.venv` to use with
the VSCode project:

1. In VSCode, navigate to:
  `View > Command Palette > Python: Select Interpreter`
2. Then, select the path to the .venv folder you created earlier.

([Source](https://code.visualstudio.com/docs/python/environments))


