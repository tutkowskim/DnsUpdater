from __future__ import annotations

import pytest

from dns_updater.config import Config, ConfigError


def test_loads_defaults() -> None:
    config = Config.from_env({"HOSTED_ZONE_ID": "zone", "RECORD_NAME": "home.example.com"})

    assert config.hosted_zone_id == "zone"
    assert config.record_name == "home.example.com"
    assert config.port == 8080
    assert config.update_interval_seconds == 300
    assert config.record_ttl_seconds == 900
    assert config.sentry_dsn is None


def test_loads_overrides() -> None:
    config = Config.from_env(
        {
            "HOSTED_ZONE_ID": "zone",
            "RECORD_NAME": "home.example.com",
            "PORT": "9000",
            "SENTRY_DSN": "https://example.invalid/1",
            "UPDATE_INTERVAL_SECONDS": "2.5",
            "RECORD_TTL_SECONDS": "60",
            "IP_CHECK_URL": "http://127.0.0.1/ip",
            "IP_CHECK_TIMEOUT_SECONDS": "3.5",
        }
    )

    assert config.port == 9000
    assert config.sentry_dsn == "https://example.invalid/1"
    assert config.update_interval_seconds == 2.5
    assert config.record_ttl_seconds == 60
    assert config.ip_check_url == "http://127.0.0.1/ip"
    assert config.ip_check_timeout_seconds == 3.5


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"HOSTED_ZONE_ID": ""}, "HOSTED_ZONE_ID"),
        ({"RECORD_NAME": ""}, "RECORD_NAME"),
        ({"PORT": "invalid"}, "PORT must be an integer"),
        ({"PORT": "0"}, "PORT must be between"),
        ({"UPDATE_INTERVAL_SECONDS": "0"}, "UPDATE_INTERVAL_SECONDS"),
        ({"UPDATE_INTERVAL_SECONDS": "invalid"}, "UPDATE_INTERVAL_SECONDS must be a number"),
        ({"RECORD_TTL_SECONDS": "0"}, "RECORD_TTL_SECONDS"),
        ({"RECORD_TTL_SECONDS": "invalid"}, "RECORD_TTL_SECONDS must be an integer"),
        ({"IP_CHECK_TIMEOUT_SECONDS": "0"}, "IP_CHECK_TIMEOUT_SECONDS"),
        ({"IP_CHECK_URL": "not-a-url"}, "IP_CHECK_URL"),
    ],
)
def test_rejects_invalid_configuration(overrides: dict[str, str], message: str) -> None:
    values = {"HOSTED_ZONE_ID": "zone", "RECORD_NAME": "home.example.com", **overrides}

    with pytest.raises(ConfigError, match=message):
        Config.from_env(values)
