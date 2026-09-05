"""Small async client for the qBittorrent WebUI API v2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from aiohttp import ClientError, ClientSession


class QBittorrentApiError(Exception):
    """Raised when qBittorrent cannot be reached or rejects a request."""


class QBittorrentApi:
    """Authenticate and query a qBittorrent WebUI instance."""

    def __init__(self, session: ClientSession, url: str, username: str, password: str) -> None:
        self._session = session
        self._base_url = url.rstrip("/")
        self._username = username
        self._password = password
        # qBittorrent rejects WebUI requests without a matching Origin/Referer.
        # This is required by the WebUI's CSRF protection, especially behind a
        # reverse proxy or when the WebUI is bound to a non-default port.
        self._headers = {"Origin": self._base_url, "Referer": self._base_url}

    async def async_login(self) -> None:
        """Log in and keep the session cookie for subsequent requests."""
        try:
            async with self._session.post(
                f"{self._base_url}/api/v2/auth/login",
                data={"username": self._username, "password": self._password},
                headers=self._headers,
            ) as response:
                body = await response.text()
        except (ClientError, TimeoutError) as err:
            raise QBittorrentApiError("Unable to connect to qBittorrent") from err

        if response.status != 200 or body.strip() != "Ok.":
            raise QBittorrentApiError("qBittorrent authentication failed")

    async def async_request(
        self,
        endpoint: str,
        *,
        method: str = "get",
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
    ) -> Any:
        """Call an API endpoint and decode its JSON response when present."""
        try:
            async with getattr(self._session, method.lower())(
                f"{self._base_url}/api/v2/{endpoint}",
                params=params,
                data=data,
                headers=self._headers,
            ) as response:
                if response.status in (401, 403):
                    raise QBittorrentApiError("qBittorrent session expired")
                if response.status >= 400:
                    raise QBittorrentApiError(f"qBittorrent returned HTTP {response.status}")
                if response.content_type == "application/json":
                    return await response.json()
                return await response.text()
        except QBittorrentApiError:
            raise
        except (ClientError, TimeoutError) as err:
            raise QBittorrentApiError("Unable to communicate with qBittorrent") from err

    async def async_get_main_data(self) -> dict[str, Any]:
        """Return transfer state and the current torrent list."""
        result = await self.async_request("sync/maindata", params={"rid": 0})
        if not isinstance(result, dict):
            raise QBittorrentApiError("Invalid response from qBittorrent")
        return result

    async def async_get_transfer_info(self) -> dict[str, Any]:
        """Return global transfer information."""
        result = await self.async_request("transfer/info")
        if not isinstance(result, dict):
            raise QBittorrentApiError("Invalid transfer response from qBittorrent")
        return result

    async def async_toggle_speed_limits(self) -> None:
        """Toggle qBittorrent's alternative speed limits."""
        await self.async_request("transfer/toggleSpeedLimitsMode", method="post")

    async def async_get_speed_limits_mode(self) -> bool:
        """Return whether alternative speed limits are active."""
        result = await self.async_request("transfer/speedLimitsMode")
        return str(result).strip() == "1"

    async def async_get_download_limit(self) -> int:
        """Return global download limit in bytes per second."""
        result = await self.async_request("transfer/downloadLimit")
        try:
            return int(result)
        except (TypeError, ValueError) as err:
            raise QBittorrentApiError("Invalid download limit response") from err

    async def async_get_upload_limit(self) -> int:
        """Return global upload limit in bytes per second."""
        result = await self.async_request("transfer/uploadLimit")
        try:
            return int(result)
        except (TypeError, ValueError) as err:
            raise QBittorrentApiError("Invalid upload limit response") from err

    async def async_set_download_limit(self, limit: int) -> None:
        """Set global download limit in bytes per second (zero means unlimited)."""
        await self.async_request(
            "transfer/setDownloadLimit", method="post", data={"limit": limit}
        )


def create_api(session: ClientSession, url: str, username: str, password: str) -> QBittorrentApi:
    """Create an API client using HA's shared HTTP session."""
    return QBittorrentApi(session, url, username, password)
