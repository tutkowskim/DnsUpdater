"""Lightweight HTTP liveness endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

logger = logging.getLogger(__name__)


class _ReusableThreadingHttpServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        body = b'{"status":"UP"}'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, message_format: str, *args: object) -> None:
        logger.debug(message_format, *args)


class HealthServer:
    """Manage the health HTTP server and its worker thread."""

    def __init__(self, port: int):
        self._server = _ReusableThreadingHttpServer(("", port), _HealthHandler)
        self._thread = Thread(target=self._server.serve_forever, name="health-server", daemon=True)

    @property
    def port(self) -> int:
        """Return the bound port, including an OS-assigned test port."""

        return self._server.server_address[1]

    def start(self) -> None:
        self._thread.start()
        logger.info("Listening on port %d", self.port)

    def stop(self) -> None:
        if self._thread.is_alive():
            self._server.shutdown()
            self._thread.join(timeout=5)
        self._server.server_close()
