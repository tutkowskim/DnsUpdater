from __future__ import annotations

from threading import Event
from unittest.mock import Mock

from dns_updater.updater import UpdateTask, run_scheduler


def test_update_task_submits_current_ip() -> None:
    ip_source = Mock()
    ip_source.get_current_ip.return_value = "203.0.113.4"
    dns_updater = Mock()
    dns_updater.upsert_a_record.return_value = {"status": "PENDING"}

    result = UpdateTask(ip_source, dns_updater, "home.example.com").run_once()

    assert result is True
    dns_updater.upsert_a_record.assert_called_once_with("203.0.113.4")


def test_update_task_contains_failures() -> None:
    ip_source = Mock()
    ip_source.get_current_ip.side_effect = RuntimeError("network failed")
    dns_updater = Mock()

    result = UpdateTask(ip_source, dns_updater, "home.example.com").run_once()

    assert result is False
    dns_updater.upsert_a_record.assert_not_called()


def test_scheduler_runs_immediately_and_until_stopped() -> None:
    stop_event = Event()
    calls = 0
    times = iter([0.0, 0.25])

    def task() -> None:
        nonlocal calls
        calls += 1
        stop_event.set()

    run_scheduler(task, 300.0, stop_event, lambda: next(times))

    assert calls == 1
