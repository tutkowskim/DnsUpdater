from __future__ import annotations

from unittest.mock import Mock, call, patch

from dns_updater.app import configure_sentry, main
from dns_updater.config import Config


def test_main_rejects_invalid_configuration() -> None:
    with (
        patch("dns_updater.app.sentry_sdk.capture_exception") as capture,
        patch("dns_updater.app.sentry_sdk.flush") as flush,
    ):
        assert main({}) == 1

    capture.assert_called_once()
    flush.assert_called_once_with(timeout=2.0)


def test_configure_sentry_is_disabled_without_dsn() -> None:
    config = Config(hosted_zone_id="zone", record_name="home.example.com")

    with patch("dns_updater.app.sentry_sdk.init") as init:
        configure_sentry(config)

    init.assert_not_called()


def test_configure_sentry_enables_tracing_and_logs() -> None:
    config = Config(
        hosted_zone_id="zone",
        record_name="home.example.com",
        sentry_dsn="https://public@example.invalid/1",
    )

    with patch("dns_updater.app.sentry_sdk.init") as init:
        configure_sentry(config)

    init.assert_called_once_with(
        dsn="https://public@example.invalid/1", traces_sample_rate=1.0, enable_logs=True
    )


def test_main_runs_and_cleans_up() -> None:
    ip_client = Mock()
    health_server = Mock()

    with (
        patch("dns_updater.app.signal.signal") as register_signal,
        patch("dns_updater.app.PublicIpClient", return_value=ip_client),
        patch("dns_updater.app.Route53RecordUpdater"),
        patch("dns_updater.app.HealthServer", return_value=health_server),
        patch("dns_updater.app.run_scheduler") as scheduler,
        patch("dns_updater.app.sentry_sdk.flush") as flush,
    ):
        result = main({"HOSTED_ZONE_ID": "zone", "RECORD_NAME": "home.example.com"})

    assert result == 0
    assert register_signal.call_count == 2
    health_server.start.assert_called_once()
    health_server.stop.assert_called_once()
    ip_client.close.assert_called_once()
    scheduler.assert_called_once()
    flush.assert_called_once_with(timeout=2.0)


def test_main_signal_handler_stops_scheduler() -> None:
    registered_handlers: list[object] = []

    def remember_handler(_signal: object, handler: object) -> None:
        registered_handlers.append(handler)

    with (
        patch("dns_updater.app.signal.signal", side_effect=remember_handler),
        patch("dns_updater.app.PublicIpClient"),
        patch("dns_updater.app.Route53RecordUpdater"),
        patch("dns_updater.app.HealthServer"),
        patch("dns_updater.app.run_scheduler") as scheduler,
        patch("dns_updater.app.sentry_sdk.flush"),
    ):
        assert main({"HOSTED_ZONE_ID": "zone", "RECORD_NAME": "home.example.com"}) == 0

    handler = registered_handlers[0]
    assert callable(handler)
    handler(15, None)
    stop_event = scheduler.call_args.args[2]
    assert stop_event.is_set()


def test_main_cleans_up_when_startup_fails() -> None:
    ip_client = Mock()
    health_server = Mock()
    health_server.start.side_effect = OSError("cannot bind")

    with (
        patch("dns_updater.app.signal.signal"),
        patch("dns_updater.app.PublicIpClient", return_value=ip_client),
        patch("dns_updater.app.Route53RecordUpdater"),
        patch("dns_updater.app.HealthServer", return_value=health_server),
        patch("dns_updater.app.sentry_sdk.capture_exception") as capture,
        patch("dns_updater.app.sentry_sdk.flush") as flush,
    ):
        result = main({"HOSTED_ZONE_ID": "zone", "RECORD_NAME": "home.example.com"})

    assert result == 1
    health_server.stop.assert_called_once()
    ip_client.close.assert_called_once()
    assert flush.call_args_list == [call(timeout=2.0), call(timeout=2.0)]
    capture.assert_called_once()
