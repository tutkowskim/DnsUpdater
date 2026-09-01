"""Scheduled DNS update workflow."""

from __future__ import annotations

import logging
from collections.abc import Callable
from threading import Event
from time import monotonic
from typing import Protocol

import sentry_sdk

logger = logging.getLogger(__name__)


class IpAddressSource(Protocol):
    def get_current_ip(self) -> str: ...


class DnsRecordUpdater(Protocol):
    def upsert_a_record(self, ip_address: str) -> object: ...


class UpdateTask:
    """Fetch the current address and submit it to DNS."""

    def __init__(
        self,
        ip_source: IpAddressSource,
        dns_updater: DnsRecordUpdater,
        record_name: str,
    ):
        self._ip_source = ip_source
        self._dns_updater = dns_updater
        self._record_name = record_name

    def run_once(self) -> bool:
        """Execute one update, returning whether it succeeded."""

        with sentry_sdk.start_transaction(name="update-task", op="scheduled") as transaction:
            try:
                logger.info("Fetching current public IP")
                ip_address = self._ip_source.get_current_ip()
                logger.info("Current public IP is %s", ip_address)
                logger.info("Updating Route 53 record %s", self._record_name)
                response = self._dns_updater.upsert_a_record(ip_address)
                logger.info("Route 53 change submitted: %s", response)
                logger.info("Successfully updated DNS entry")
                transaction.set_status("ok")
                return True
            except Exception as exc:
                logger.exception("Update task failed")
                transaction.set_status("internal_error")
                sentry_sdk.capture_exception(exc)
                return False


def run_scheduler(
    task: Callable[[], object],
    interval_seconds: float,
    stop_event: Event,
    clock: Callable[[], float] = monotonic,
) -> None:
    """Run immediately and then at a fixed rate until stopped."""

    next_run = clock()
    while not stop_event.is_set():
        task()
        next_run += interval_seconds
        stop_event.wait(max(0.0, next_run - clock()))
