from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from dns_updater.health import HealthServer


def test_health_endpoint() -> None:
    server = HealthServer(0)
    server.start()
    try:
        with urlopen(f"http://127.0.0.1:{server.port}/health", timeout=2) as response:  # noqa: S310
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json"
            assert json.load(response) == {"status": "UP"}
    finally:
        server.stop()


def test_unknown_endpoint_returns_not_found() -> None:
    server = HealthServer(0)
    server.start()
    try:
        with pytest.raises(HTTPError) as error:
            urlopen(f"http://127.0.0.1:{server.port}/missing", timeout=2)  # noqa: S310
        assert error.value.code == 404
    finally:
        server.stop()
