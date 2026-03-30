# Atoti Project Template

This template can be used to start Atoti projects where the goal is to [go into production rather than prototyping in a notebook](https://docs.atoti.io/latest/deployment/going_from_a_notebook_to_an_app.html).

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

To start the app:

```bash
uv run python -m app
```

To start the app in Docker with [Jaeger](https://www.jaegertracing.io) to observe traces:

```bash
docker compose up --build
```

Other useful commands can be found in [`test.yml`](.github/workflows/test.yml).

## Deployment

This repository automatically deploys to [AWS ECS](https://aws.amazon.com/ecs/).
To deploy somewhere else, delete [`task-definition.json`](task-definition.json) and adapt [`deploy.yml`](.github/workflows/deploy.yml).
