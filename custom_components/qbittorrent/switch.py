"""qBittorrent controls."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API, COORDINATOR, DOMAIN
from .entity import QBittorrentEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the alternative speed limits switch."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([QBittorrentSpeedLimitsSwitch(data[COORDINATOR], data[API])])


class QBittorrentSpeedLimitsSwitch(QBittorrentEntity, SwitchEntity):
    """Toggle qBittorrent alternative speed limits."""

    _attr_name = "Alternative speed limits"
    _attr_icon = "mdi:speedometer-slow"

    def __init__(self, coordinator, api) -> None:
        super().__init__(coordinator, "alternative_speed_limits")
        self._api = api

    @property
    def is_on(self) -> bool:
        return self.coordinator.data["alt_speed_limits"]

    async def async_turn_on(self, **kwargs) -> None:
        if not self.is_on:
            await self._api.async_toggle_speed_limits()
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        if self.is_on:
            await self._api.async_toggle_speed_limits()
            await self.coordinator.async_request_refresh()
