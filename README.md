# DnsUpdater

DnsUpdater keeps an Amazon Route 53 `A` record synchronized with the machine's public IPv4
address. It updates immediately on startup, repeats every five minutes by default, and exposes a
small liveness endpoint for container orchestration.

## Configuration

AWS credentials use boto3's standard credential chain, such as environment variables, a shared
credentials file, or an attached instance/task role.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `HOSTED_ZONE_ID` | Yes | — | Route 53 hosted zone ID |
| `RECORD_NAME` | Yes | — | DNS record to update |
| `PORT` | No | `8080` | Health server port |
| `SENTRY_DSN` | No | — | Enables Sentry errors, logs, and traces |
| `UPDATE_INTERVAL_SECONDS` | No | `300` | Fixed-rate update interval |
| `RECORD_TTL_SECONDS` | No | `900` | Route 53 record TTL |
| `IP_CHECK_URL` | No | `https://checkip.amazonaws.com/` | Public-IP service |
| `IP_CHECK_TIMEOUT_SECONDS` | No | `10` | Public-IP request timeout |

## Development

Install the pinned Python version and locked dependencies:

```shell
uv python install
uv sync
```

Run the quality checks:

```shell
uv run ruff check .
uv run mypy
uv run pytest
```

Run the service:

```shell
HOSTED_ZONE_ID=Z123456789 RECORD_NAME=home.example.com uv run dns-updater
```

The liveness endpoint is available at `GET /health` and returns `{"status":"UP"}`.

## Container

```shell
docker build -t dns-updater .
docker run --rm -p 8080:8080 \
  -e HOSTED_ZONE_ID=Z123456789 \
  -e RECORD_NAME=home.example.com \
  dns-updater
```
