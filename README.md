# Atoti Project Template

This template can be used to start Atoti projects where the goal is to [go into production rather than prototyping in a notebook](https://docs.activeviam.com/engine/python-sdk/6.2/getting_started/deployment/going_from_a_notebook_to_an_app).

On top of the `atoti` package, it comes with:

- Dependency management with [uv](https://docs.astral.sh/uv)
- Config management with [Pydantic](https://docs.pydantic.dev/2.6/concepts/pydantic_settings)
- Testing with [pytest](https://docs.pytest.org)
- Observability with [OpenTelemetry](https://opentelemetry.io/docs/languages/python)
- Type checking with [ty](https://docs.astral.sh/ty)
- Formatting and linting with [Ruff](https://docs.astral.sh/ruff)
- Continuous testing with [GitHub Actions](https://github.com/features/actions)

## Usage

### Installation

- [Install `uv`](https://docs.astral.sh/uv/getting-started/installation)
- Install the dependencies:

  ```bash
  uv sync
  ```

### Commands

Start the app:

- with Docker and [Grafana OpenTelemetry LGTM](https://grafana.com/docs/opentelemetry/docker-lgtm):

  ```bash
  docker compose up --build
  ```

- without them:

  ```bash
  uv run python -m app
  ```

Other useful commands can be found in [`test.yml`](.github/workflows/test.yml).

## Deployment

This repository automatically deploys to [AWS ECS](https://aws.amazon.com/ecs/).
To deploy somewhere else, delete [`task-definition.json`](task-definition.json) and adapt [`deploy.yml`](.github/workflows/deploy.yml).
