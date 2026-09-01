"""Application composition and lifecycle."""

from __future__ import annotations

import logging
import signal
from collections.abc import Mapping
from threading import Event
from types import FrameType

import sentry_sdk

from dns_updater.config import Config
from dns_updater.health import HealthServer
from dns_updater.ip_check import PublicIpClient
from dns_updater.route53 import Route53RecordUpdater
from dns_updater.updater import UpdateTask, run_scheduler

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s %(name)s - %(message)s",
    )


def configure_sentry(config: Config) -> None:
    if config.sentry_dsn is None:
        logger.info("Sentry disabled (missing SENTRY_DSN)")
        return

    sentry_sdk.init(dsn=config.sentry_dsn, traces_sample_rate=1.0, enable_logs=True)
    logger.info("Sentry enabled")


def main(environ: Mapping[str, str] | None = None) -> int:
    """Start the application and block until a termination signal."""

    configure_logging()
    try:
        config = Config.from_env(environ)
        configure_sentry(config)
        stop_event = Event()

        def request_shutdown(signum: int, _frame: FrameType | None) -> None:
            logger.info("Received signal %d; shutting down", signum)
            stop_event.set()

        signal.signal(signal.SIGTERM, request_shutdown)
        signal.signal(signal.SIGINT, request_shutdown)

        ip_client = PublicIpClient(config.ip_check_url, config.ip_check_timeout_seconds)
        health_server: HealthServer | None = None
        try:
            dns_updater = Route53RecordUpdater(
                config.hosted_zone_id,
                config.record_name,
                config.record_ttl_seconds,
            )
            task = UpdateTask(ip_client, dns_updater, config.record_name)
            health_server = HealthServer(config.port)
            health_server.start()
            logger.info(
                "Scheduled update task with initial delay 0 seconds and period %.3f seconds",
                config.update_interval_seconds,
            )
            run_scheduler(task.run_once, config.update_interval_seconds, stop_event)
        finally:
            if health_server is not None:
                health_server.stop()
            ip_client.close()
            sentry_sdk.flush(timeout=2.0)
        return 0
    except Exception as exc:
        logger.exception("Fatal error during startup")
        sentry_sdk.capture_exception(exc)
        sentry_sdk.flush(timeout=2.0)
        return 1
