"""Sensors exposed by qBittorrent."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR, DOMAIN
from .coordinator import QBittorrentCoordinator
from .entity import QBittorrentEntity


@dataclass(frozen=True)
class SensorDescription:
    key: str
    name: str
    icon: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT


SENSORS = (
    SensorDescription("status", "Status", "mdi:transit-connection-variant", state_class=None),
    SensorDescription("total", "Total torrents", "mdi:download-multiple", state_class=None),
    SensorDescription("downloading", "Downloading", "mdi:download", state_class=None),
    SensorDescription("seeding", "Seeding", "mdi:upload", state_class=None),
    SensorDescription("paused", "Paused", "mdi:pause-circle", state_class=None),
    SensorDescription("completed", "Completed", "mdi:check-circle", state_class=None),
    SensorDescription(
        "download_speed", "Download speed", "mdi:download", UnitOfDataRate.MEGABYTES_PER_SECOND
    ),
    SensorDescription(
        "upload_speed", "Upload speed", "mdi:upload", UnitOfDataRate.MEGABYTES_PER_SECOND
    ),
    SensorDescription(
        "free_space",
        "Free space",
        "mdi:harddisk",
        UnitOfInformation.GIGABYTES,
        SensorDeviceClass.DATA_SIZE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up qBittorrent sensors."""
    coordinator: QBittorrentCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    async_add_entities(QBittorrentSensor(coordinator, description) for description in SENSORS)


class QBittorrentSensor(QBittorrentEntity, SensorEntity):
    """A qBittorrent statistic sensor."""

    def __init__(self, coordinator: QBittorrentCoordinator, description: SensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC if description.key == "free_space" else None
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if self.entity_description.key == "status":
            connection = data["transfer"].get("connection_status", "disconnected")
            if connection != "connected":
                return connection.title()
            download = data["transfer"].get("dl_info_speed", 0)
            upload = data["transfer"].get("up_info_speed", 0)
            if download and upload:
                return "Downloading/Seeding"
            if download:
                return "Downloading"
            if upload:
                return "Seeding"
            return "Idle"
        if self.entity_description.key in data["counts"]:
            return data["counts"][self.entity_description.key]
        transfer = data["transfer"]
        if self.entity_description.key == "download_speed":
            return round(transfer.get("dl_info_speed", 0) / 1_000_000, 2)
        if self.entity_description.key == "upload_speed":
            return round(transfer.get("up_info_speed", 0) / 1_000_000, 2)
        if self.entity_description.key == "free_space":
            return round(transfer.get("free_space_on_disk", 0) / 1_000_000_000, 2)
        return None
