# SQL AI agent tutorials

This folder contains the executable notebooks in the tutorial supporting
repository. Run Jupyter from the repository root so each notebook
can resolve the shared `data/` and `docker/` folders.

The SQL AI agent tutorial series uses DuckDB. The PostgreSQL notebook is an
optional alternative for readers who prefer PostgreSQL; no later tutorial
requires it.

The DuckDB notebook stores its database in the directory defined by
`DUCKDB_DATABASES_PATH`. On a Mac that uses zsh, add the following setting to
`~/.zshenv`, reload the file, and create the directory:

```bash
export DUCKDB_DATABASES_PATH="$HOME/databases/duckdb"
source ~/.zshenv
mkdir -p "$DUCKDB_DATABASES_PATH"
```

On Linux, add the export to the startup file for the active shell. On Windows
PowerShell, create the equivalent persistent user-level variable and directory:

```powershell
[Environment]::SetEnvironmentVariable("DUCKDB_DATABASES_PATH", "$HOME\databases\duckdb", "User")
New-Item -ItemType Directory -Force "$HOME\databases\duckdb"
```

## Available tutorials

- [`03a_duckdb_settings.ipynb`](03a_duckdb_settings.ipynb) — Set up the data
  with DuckDB and Ibis
- [`03a_postgresql_settings.ipynb`](03a_postgresql_settings.ipynb) — Optional:
  set up the data with PostgreSQL and Ibis in the Dev Container

## Option 1: run with a local virtual environment

### Prerequisites

- Python 3.12, or [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

I recommend uv for the local setup because it can obtain Python 3.12 and
create the environment. If we prefer not to install uv, Python's
standard-library `venv` module with pip provides the alternative below.

### Recommended: use uv

From the repository root, create a Python 3.12 virtual environment, activate
it, and install the declared dependencies:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install --no-cache-dir -r docker/requirements.txt
```

The `uv venv` command creates the environment in `.venv` and installs Python
3.12 if necessary.

### Alternative: use venv and pip

This method does not require uv. First, confirm that `python3` resolves to
Python 3.12. Then create the virtual environment with Python's standard-library
`venv` module and install the declared dependencies with pip:

```bash
python3 --version
# Python 3.12.x
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r docker/requirements.txt
```

On Windows PowerShell, confirm the version with `py -3.12 --version`, create the
environment with `py -3.12 -m venv .venv`, and activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

The Windows commands have been reviewed but have not been run as part of this
tutorial's verification.

The environment setup is complete after the dependencies are installed. To run
the supporting notebook interactively, start Jupyter as a separate step:

```bash
jupyter notebook tutorials/03a_duckdb_settings.ipynb
```

This command opens the notebook; it does not create or configure the virtual
environment. For either local method, stop Jupyter with `Ctrl+C` and leave the
environment with:

```bash
deactivate
```

## Option 2: run with Docker and VS Code Dev Containers

This option uses `.devcontainer/devcontainer.json` and `docker-compose.yaml`.
It does not require a local Python installation.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- The [Dev Containers
  extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- A local clone of this repository

The Docker environment supports both database examples. DuckDB remains the
default for the tutorial series, while PostgreSQL is an optional alternative.

### Database settings for the Docker option

Docker Compose needs the two database paths when we use the Docker environment.
It includes a PostgreSQL service alongside Python even when the DuckDB notebook
is the example we plan to run. The Compose file provides local defaults for the
PostgreSQL connection values, which we can override if needed.

When Docker Compose starts the Python service, it mounts the host directory
defined by `DUCKDB_DATABASES_PATH` at `/databases/duckdb` in the container.
The notebook receives that container path through the same environment-variable
name. PostgreSQL uses its own host directory for persistent service data.

On a Mac that uses zsh, add the required storage variables and any optional
PostgreSQL overrides to `~/.zshenv` so they persist for the current user:

```bash
export DUCKDB_DATABASES_PATH="$HOME/databases/duckdb"
export POSTGRES_DATABASES_PATH="$HOME/databases/postgres"

# Optional PostgreSQL overrides
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="password"
export POSTGRES_DB="my_db"
```

After saving the file, quit any running VS Code instance completely, reload the
file, create the database directory, and launch VS Code from the same terminal:

```bash
source ~/.zshenv
mkdir -p "$DUCKDB_DATABASES_PATH"
mkdir -p "$POSTGRES_DATABASES_PATH/sql-ai-agent"
code .
```

The `mkdir` commands create the local directories that Docker mounts into the
containers. DuckDB writes `sql-ai-agent.duckdb` under
`DUCKDB_DATABASES_PATH`, while PostgreSQL writes its database files under the
`sql-ai-agent` project directory within `POSTGRES_DATABASES_PATH`. The data
remains available after the containers are stopped or recreated. Deleting
either local directory also deletes its persisted database data.

The sample password is a plain-text local development default; do not replace
it with a real or shared database password. On Linux, add the same exports to
the startup file for the active shell, such as `~/.bashrc` for Bash or
`~/.zshenv` for zsh, then reload that file and launch VS Code from the same
terminal after quitting any running VS Code instance.

On Windows PowerShell, create persistent user-level variables as follows:

```powershell
[Environment]::SetEnvironmentVariable("DUCKDB_DATABASES_PATH", "$HOME\databases\duckdb", "User")
[Environment]::SetEnvironmentVariable("POSTGRES_DATABASES_PATH", "$HOME\databases\postgres", "User")
[Environment]::SetEnvironmentVariable("POSTGRES_USER", "postgres", "User")
[Environment]::SetEnvironmentVariable("POSTGRES_PASSWORD", "password", "User")
[Environment]::SetEnvironmentVariable("POSTGRES_DB", "my_db", "User")
New-Item -ItemType Directory -Force "$HOME\databases\duckdb"
New-Item -ItemType Directory -Force "$HOME\databases\postgres\sql-ai-agent"
```

Close and reopen PowerShell and VS Code after setting the Windows variables,
then launch the repository with `code .` so VS Code inherits them.

When prompted in VS Code, select **Reopen in Container**. We can also open the
Command Palette and select **Dev Containers: Reopen in Container**. Docker
Compose builds the Python service from `docker/Dockerfile_Dev`, starts it with
the PostgreSQL service, mounts the repository at `/workspace`, and selects the
Python 3.12.11 environment at
`/opt/sql-ai-agent-dev/bin/python3`.

### DuckDB notebook: the tutorial-series path

Open `tutorials/03a_duckdb_settings.ipynb` and run its cells in VS Code. This
is the same DuckDB example used by the local virtual-environment option and is
the database path used by the tutorial series.

### PostgreSQL notebook: an optional Docker example

Readers who prefer PostgreSQL can open
`tutorials/03a_postgresql_settings.ipynb` and run its cells instead. The
notebook is tested with the PostgreSQL service provided by this Docker setup,
but it is not required for this or later tutorials.

PostgreSQL does not inherently require Docker. It can be installed locally or
hosted elsewhere, but configuring those alternatives is outside this
tutorial's scope. The supplied PostgreSQL notebook assumes the Compose
hostname and environment variables documented above.

This tutorial does not invoke a model, so the model API keys can remain unset.
When finished, reopen a local terminal in the repository root and stop the
services explicitly; closing VS Code does not stop them because the Dev
Container uses `"shutdownAction": "none"`:

```bash
docker compose down
```

## Troubleshooting

- **The dataset cannot be found:** Start Jupyter from the repository root and
  confirm that `data/Air_Traffic_Passenger_Statistics_20260905.csv` exists.
- **The Dev Container does not start:** Confirm Docker Desktop is running and
  that the four Compose variables were set before VS Code was launched.
- **The DuckDB database cannot be created:** Confirm that
  `DUCKDB_DATABASES_PATH` is set and that its directory exists and is writable.
- **The DuckDB table remains after a restart:** This is expected. Its data is
  stored in `sql-ai-agent.duckdb` under `$DUCKDB_DATABASES_PATH`.
- **The PostgreSQL notebook cannot connect:** Confirm that it is running inside
  the Dev Container and that the PostgreSQL service is healthy with
  `docker compose ps`.
- **The PostgreSQL table remains after a restart:** This is expected. Its data
  is stored under `$POSTGRES_DATABASES_PATH/sql-ai-agent` on the host.

## License

This tutorial is licensed under a [Creative Commons
Attribution-NonCommercial-ShareAlike 4.0
International](https://creativecommons.org/licenses/by-nc-sa/4.0/)
License.
