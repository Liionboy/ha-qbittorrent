"""Constants for the qBittorrent integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "qbittorrent"
PLATFORMS: list[Platform] = [Platform.NUMBER, Platform.SENSOR, Platform.SWITCH]

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_URL = "http://localhost:8080"

COORDINATOR = "coordinator"
API = "api"

ATTR_TORRENT_COUNT = "torrent_count"
ATTR_DOWNLOADING = "downloading"
ATTR_SEEDING = "seeding"
ATTR_PAUSED = "paused"
ATTR_COMPLETED = "completed"
ATTR_VERSION = "version"

