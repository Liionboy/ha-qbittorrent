"""Data coordinator for qBittorrent."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import QBittorrentApi, QBittorrentApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class QBittorrentCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch qBittorrent data once for all entities."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: QBittorrentApi) -> None:
        self.api = api
        self.entry = entry
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            await self.api.async_login()
            main = await self.api.async_get_main_data()
            transfer = await self.api.async_get_transfer_info()
            alt_speed_limits = await self.api.async_get_speed_limits_mode()
            download_limit = await self.api.async_get_download_limit()
        except QBittorrentApiError as err:
            raise UpdateFailed(str(err)) from err

        torrents = list(main.get("torrents", {}).values())
        counts = {
            "total": len(torrents),
            "downloading": sum(_is_downloading(torrent) for torrent in torrents),
            "seeding": sum(_is_seeding(torrent) for torrent in torrents),
            "paused": sum(_is_paused(torrent) for torrent in torrents),
            "completed": sum(float(torrent.get("progress", 0)) >= 1 for torrent in torrents),
        }
        return {
            "main": main,
            "transfer": transfer,
            "counts": counts,
            "alt_speed_limits": alt_speed_limits,
            "download_limit": download_limit,
        }


def _is_downloading(torrent: dict[str, Any]) -> bool:
    return torrent.get("state") in {"downloading", "metaDL", "forcedDL", "stalledDL"}


def _is_seeding(torrent: dict[str, Any]) -> bool:
    return torrent.get("state") in {"uploading", "stalledUP", "forcedUP", "queuedUP"}


def _is_paused(torrent: dict[str, Any]) -> bool:
    return torrent.get("state") in {"pausedDL", "pausedUP", "stoppedDL", "stoppedUP"}
