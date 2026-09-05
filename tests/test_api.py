"""Protocol-level tests for the qBittorrent API client."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest

_AIOHTTP_STUB = types.ModuleType("aiohttp")
_AIOHTTP_STUB.ClientError = type("ClientError", (Exception,), {})
_AIOHTTP_STUB.ClientSession = object
sys.modules.setdefault("aiohttp", _AIOHTTP_STUB)

_API_SPEC = importlib.util.spec_from_file_location(
    "qbittorrent_api", Path(__file__).parents[1] / "custom_components/qbittorrent/api.py"
)
_API_MODULE = importlib.util.module_from_spec(_API_SPEC)
assert _API_SPEC.loader is not None
_API_SPEC.loader.exec_module(_API_MODULE)
QBittorrentApi = _API_MODULE.QBittorrentApi
QBittorrentApiError = _API_MODULE.QBittorrentApiError


class FakeResponse:
    def __init__(self, status=200, body="Ok.", json_body=None):
        self.status = status
        self._body = body
        self._json_body = json_body
        self.content_type = "application/json" if json_body is not None else "text/plain"

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def text(self):
        return self._body

    async def json(self):
        return self._json_body


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return self.responses.pop(0)

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return self.responses.pop(0)


class QBittorrentApiTests(unittest.TestCase):
    def test_login_and_main_data(self):
        session = FakeSession([FakeResponse(), FakeResponse(json_body={"torrents": {}})])
        api = QBittorrentApi(session, "http://qbit:8080", "user", "password")

        async def run():
            await api.async_login()
            return await api.async_get_main_data()

        self.assertEqual(asyncio.run(run()), {"torrents": {}})
        self.assertEqual(session.calls[0][1], "http://qbit:8080/api/v2/auth/login")
        self.assertEqual(session.calls[0][2]["data"]["username"], "user")
        self.assertEqual(session.calls[1][2]["params"], {"rid": 0})

    def test_login_rejects_non_ok_response(self):
        api = QBittorrentApi(FakeSession([FakeResponse(body="Fails."),]), "http://qbit", "u", "p")

        with self.assertRaises(QBittorrentApiError):
            asyncio.run(api.async_login())

    def test_http_error_is_reported(self):
        api = QBittorrentApi(FakeSession([FakeResponse(status=403)]), "http://qbit", "u", "p")

        with self.assertRaises(QBittorrentApiError):
            asyncio.run(api.async_request("transfer/info"))


if __name__ == "__main__":
    unittest.main()
