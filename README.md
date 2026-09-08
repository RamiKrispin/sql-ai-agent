# SQL AI Agent

## Setting Up Environment

This project runs inside a Docker container using the [VS Code Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. The container includes a Python virtual environment, PostgreSQL database, and all required dependencies.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension installed

### Environment Variables

The container expects the following environment variables to be set on your local machine (e.g., in your `~/.zshrc` or `~/.bashrc`):

**API Keys** (required for LLM functionality):

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |

**PostgreSQL** (optional, defaults provided):

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_DB` | `my_db` | Database name |

**Database storage** (required):

| Variable | Description |
|---|---|
| `DUCKDB_DATABASES_PATH` | Local path for storing persistent DuckDB database files (e.g., `~/databases/duckdb`) |
| `POSTGRES_DATABASES_PATH` | Local path for persisting PostgreSQL data across container restarts (e.g., `~/databases/postgres`) |

On a Mac that uses zsh, add these values to `~/.zshenv`:

```bash
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export DUCKDB_DATABASES_PATH="$HOME/databases/duckdb"
export POSTGRES_DATABASES_PATH="$HOME/databases/postgres"
```

Then reload the file (`source ~/.zshenv`) or restart your terminal.

Create the host directories before starting the containers:

```bash
mkdir -p "$DUCKDB_DATABASES_PATH"
mkdir -p "$POSTGRES_DATABASES_PATH/sql-ai-agent"
```

### Launching the Container

1. Clone this repository and open it in VS Code
2. When prompted, click **Reopen in Container** — or open the Command Palette (`Cmd+Shift+P`) and select **Dev Containers: Reopen in Container**
3. VS Code will build and start the container using the `docker-compose.yaml` configuration. This spins up two services:
   - **python** — the development environment with Python 3.11, mounted at `/workspace/`
   - **postgres** — a PostgreSQL 15 database, accessible from the python container at `postgres:5432`
4. Once the container is running, the Python virtual environment is automatically activated at `/opt/sql-ai-agent-dev/`

### Project Structure

```
.devcontainer/
  devcontainer.json      # Dev container configuration
docker/
  Dockerfile_Base        # Base image (Ubuntu + system dependencies + Quarto)
  Dockerfile_Dev         # Dev image (Python venv + packages)
  install_dependencies.sh # System-level dependencies
  install_uv.sh          # Python environment setup via uv
  install_quarto.sh      # Quarto installation
  requirements.txt       # Python package dependencies
  build_base_docker.sh   # Build script for the base image
  build_dev_docker.sh    # Build script for the dev image
docker-compose.yaml      # Multi-service container orchestration
tutorials/
  README.md              # Docker and virtual-environment instructions
  03_data.ipynb          # Data setup with DuckDB and Ibis
```

## License

This template is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) License.
