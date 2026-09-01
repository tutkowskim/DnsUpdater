"""Environment-backed application configuration."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse


class ConfigError(ValueError):
    """Raised when application configuration is invalid."""


@dataclass(frozen=True, slots=True)
class Config:
    """Validated runtime configuration."""

    hosted_zone_id: str
    record_name: str
    port: int = 8080
    sentry_dsn: str | None = None
    update_interval_seconds: float = 300.0
    record_ttl_seconds: int = 900
    ip_check_url: str = "https://checkip.amazonaws.com/"
    ip_check_timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Config:
        """Load and validate configuration from environment variables."""

        values = os.environ if environ is None else environ
        missing = [name for name in ("HOSTED_ZONE_ID", "RECORD_NAME") if not values.get(name)]
        if missing:
            joined = ", ".join(missing)
            raise ConfigError(f"Missing required environment variable(s): {joined}")

        port = _parse_int(values, "PORT", 8080)
        if not 1 <= port <= 65535:
            raise ConfigError("PORT must be between 1 and 65535")

        interval = _parse_float(values, "UPDATE_INTERVAL_SECONDS", 300.0)
        if interval <= 0:
            raise ConfigError("UPDATE_INTERVAL_SECONDS must be greater than zero")

        ttl = _parse_int(values, "RECORD_TTL_SECONDS", 900)
        if ttl <= 0:
            raise ConfigError("RECORD_TTL_SECONDS must be greater than zero")

        timeout = _parse_float(values, "IP_CHECK_TIMEOUT_SECONDS", 10.0)
        if timeout <= 0:
            raise ConfigError("IP_CHECK_TIMEOUT_SECONDS must be greater than zero")

        ip_check_url = values.get("IP_CHECK_URL", "https://checkip.amazonaws.com/")
        parsed_url = urlparse(ip_check_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ConfigError("IP_CHECK_URL must be an absolute HTTP or HTTPS URL")

        sentry_dsn = values.get("SENTRY_DSN") or None
        return cls(
            hosted_zone_id=values["HOSTED_ZONE_ID"],
            record_name=values["RECORD_NAME"],
            port=port,
            sentry_dsn=sentry_dsn,
            update_interval_seconds=interval,
            record_ttl_seconds=ttl,
            ip_check_url=ip_check_url,
            ip_check_timeout_seconds=timeout,
        )


def _parse_int(values: Mapping[str, str], name: str, default: int) -> int:
    raw_value = values.get(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc


def _parse_float(values: Mapping[str, str], name: str, default: float) -> float:
    raw_value = values.get(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number") from exc
