from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from dns_updater.ip_check import PublicIpClient


def make_client(response: httpx.Response) -> PublicIpClient:
    transport = httpx.MockTransport(lambda _request: response)
    return PublicIpClient("https://ip.example", 1.0, httpx.Client(transport=transport))


def test_returns_a_valid_ipv4_address() -> None:
    client = make_client(httpx.Response(200, text="203.0.113.4\n"))

    assert client.get_current_ip() == "203.0.113.4"


@pytest.mark.parametrize("body", ["", "not-an-ip", "2001:db8::1"])
def test_rejects_invalid_responses(body: str) -> None:
    client = make_client(httpx.Response(200, text=body))

    with pytest.raises(ValueError):
        client.get_current_ip()


def test_rejects_http_error() -> None:
    client = make_client(httpx.Response(503, text="unavailable"))

    with pytest.raises(httpx.HTTPStatusError):
        client.get_current_ip()


def test_closes_an_internally_created_client() -> None:
    with patch("dns_updater.ip_check.httpx.Client") as client_type:
        client = PublicIpClient("https://ip.example", 1.0)
        client.close()

    client_type.return_value.close.assert_called_once()
