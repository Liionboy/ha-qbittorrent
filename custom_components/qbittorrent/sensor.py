"""Sensors exposed by qBittorrent."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR, DOMAIN
from .coordinator import QBittorrentCoordinator
from .entity import QBittorrentEntity


SENSORS = (
    SensorEntityDescription(
        key="status", name="Status", icon="mdi:transit-connection-variant"
    ),
    SensorEntityDescription(
        key="total", name="Total torrents", icon="mdi:download-multiple"
    ),
    SensorEntityDescription(key="downloading", name="Downloading", icon="mdi:download"),
    SensorEntityDescription(key="seeding", name="Seeding", icon="mdi:upload"),
    SensorEntityDescription(key="paused", name="Paused", icon="mdi:pause-circle"),
    SensorEntityDescription(key="completed", name="Completed", icon="mdi:check-circle"),
    SensorEntityDescription(key="active", name="Active torrents", icon="mdi:play-circle"),
    SensorEntityDescription(key="stalled", name="Stalled torrents", icon="mdi:pause-octagon"),
    SensorEntityDescription(key="errored", name="Errored torrents", icon="mdi:alert-circle"),
    SensorEntityDescription(key="dht_nodes", name="DHT nodes", icon="mdi:lan-connect"),
    SensorEntityDescription(
        key="session_downloaded",
        name="Session downloaded",
        icon="mdi:download-network",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="session_uploaded",
        name="Session uploaded",
        icon="mdi:upload-network",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_size",
        name="Total torrent size",
        icon="mdi:database",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="download_speed",
        name="Download speed",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="upload_speed",
        name="Upload speed",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="download_limit",
        name="Download limit",
        icon="mdi:download-lock",
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
    ),
    SensorEntityDescription(
        key="upload_limit",
        name="Upload limit",
        icon="mdi:upload-lock",
        native_unit_of_measurement=UnitOfDataRate.MEGABYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
    ),
    SensorEntityDescription(
        key="free_space",
        name="Free space",
        icon="mdi:harddisk",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up qBittorrent sensors."""
    coordinator: QBittorrentCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    async_add_entities([QBittorrentSensor(coordinator, description) for description in SENSORS])


class QBittorrentSensor(QBittorrentEntity, SensorEntity):
    """A qBittorrent statistic sensor."""

    def __init__(
        self, coordinator: QBittorrentCoordinator, description: SensorEntityDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
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
        if (
            self.entity_description.key in data["counts"]
            and self.entity_description.key != "total_size"
        ):
            return data["counts"][self.entity_description.key]
        transfer = data["transfer"]
        if self.entity_description.key == "download_speed":
            return round(transfer.get("dl_info_speed", 0) / 1_000_000, 2)
        if self.entity_description.key == "upload_speed":
            return round(transfer.get("up_info_speed", 0) / 1_000_000, 2)
        if self.entity_description.key == "dht_nodes":
            return transfer.get("dht_nodes", 0)
        if self.entity_description.key == "session_downloaded":
            return round(transfer.get("dl_info_data", 0) / 1_000_000_000, 2)
        if self.entity_description.key == "session_uploaded":
            return round(transfer.get("up_info_data", 0) / 1_000_000_000, 2)
        if self.entity_description.key == "total_size":
            return round(data["counts"].get("total_size", 0) / 1_000_000_000, 2)
        if self.entity_description.key == "download_limit":
            return round(data.get("download_limit", 0) / 1_000_000, 2)
        if self.entity_description.key == "upload_limit":
            return round(data.get("upload_limit", 0) / 1_000_000, 2)
        if self.entity_description.key == "free_space":
            # qBittorrent exposes this field in sync/maindata.server_state.
            # Keep the transfer.info fallback for older/non-standard servers.
            server_state = data["main"].get("server_state", {})
            free_space = server_state.get("free_space_on_disk")
            if free_space is None:
                free_space = transfer.get("free_space_on_disk")
            if free_space is None:
                return None
            return round(float(free_space) / 1_000_000_000, 2)
        return None

    @property
    def extra_state_attributes(self):
        """Return useful global qBittorrent data on the status sensor."""
        if self.entity_description.key != "status":
            return None

        data = self.coordinator.data
        transfer = data["transfer"]
        counts = data["counts"]
        return {
            "connection_status": transfer.get("connection_status"),
            "dht_nodes": transfer.get("dht_nodes", 0),
            "queueing": transfer.get("queueing"),
            "alternative_speed_limits": data.get("alt_speed_limits", False),
            "download_limit_mb_s": round(data.get("download_limit", 0) / 1_000_000, 2),
            "upload_limit_mb_s": round(data.get("upload_limit", 0) / 1_000_000, 2),
            "session_downloaded_gb": round(transfer.get("dl_info_data", 0) / 1_000_000_000, 2),
            "session_uploaded_gb": round(transfer.get("up_info_data", 0) / 1_000_000_000, 2),
            "active_torrents": counts["active"],
            "stalled_torrents": counts["stalled"],
            "errored_torrents": counts["errored"],
            "total_size_gb": round(counts["total_size"] / 1_000_000_000, 2),
        }
