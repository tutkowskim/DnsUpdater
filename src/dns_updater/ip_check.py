"""Public IP address discovery."""

from __future__ import annotations

from ipaddress import IPv4Address

import httpx


class PublicIpClient:
    """Retrieve and validate the host's public IPv4 address."""

    def __init__(self, url: str, timeout_seconds: float, client: httpx.Client | None = None):
        self._url = url
        self._client = client or httpx.Client()
        self._owns_client = client is None
        self._timeout_seconds = timeout_seconds

    def get_current_ip(self) -> str:
        """Return the current public IPv4 address."""

        response = self._client.get(self._url, timeout=self._timeout_seconds)
        response.raise_for_status()
        value = response.text.strip()
        if not value:
            raise ValueError("Public IP service returned an empty response")
        return str(IPv4Address(value))

    def close(self) -> None:
        """Close an internally-created HTTP client."""

        if self._owns_client:
            self._client.close()
