"""Shared qBittorrent entity helpers."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import QBittorrentCoordinator


class QBittorrentEntity(CoordinatorEntity[QBittorrentCoordinator]):
    """Base entity with common device metadata."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: QBittorrentCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"

    @property
    def device_info(self):
        return {
            "identifiers": {("qbittorrent", self.coordinator.entry.entry_id)},
            "name": "qBittorrent",
            "manufacturer": "qBittorrent project",
            "model": "WebUI",
            "configuration_url": self.coordinator.entry.data["url"],
        }
