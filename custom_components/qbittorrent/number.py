"""qBittorrent global download limit control."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API, COORDINATOR, DOMAIN
from .entity import QBittorrentEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the global download limit."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([QBittorrentDownloadLimit(data[COORDINATOR], data[API])])


class QBittorrentDownloadLimit(QBittorrentEntity, NumberEntity):
    """Global qBittorrent download limit in MB/s."""

    _attr_name = "Global download limit"
    _attr_icon = "mdi:download-lock"
    _attr_native_min_value = 0
    _attr_native_max_value = 1000
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = UnitOfDataRate.MEGABYTES_PER_SECOND

    def __init__(self, coordinator, api) -> None:
        super().__init__(coordinator, "global_download_limit")
        self._api = api

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data["download_limit"] / 1_000_000, 2)

    async def async_set_native_value(self, value: float) -> None:
        await self._api.async_set_download_limit(round(value * 1_000_000))
        await self.coordinator.async_request_refresh()
