# qBittorrent for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Validate](https://github.com/Liionboy/ha-qbittorrent/actions/workflows/validate.yml/badge.svg)](https://github.com/Liionboy/ha-qbittorrent/actions/workflows/validate.yml)

Modern Home Assistant custom integration for the qBittorrent WebUI API v2. It is a clean-room implementation inspired by the older YAML component at [radsonpatrick/qbittorrent_custom_component](https://github.com/radsonpatrick/qbittorrent_custom_component), with no code copied from it.

Current release: **1.1.1**.

## Features

- UI configuration through **Settings → Devices & services → Add integration**.
- Sensors for total, downloading, seeding, paused and completed torrents.
- Sensors for download/upload speed, active, stalled and errored torrents, DHT
  nodes, session traffic, total torrent size, global limits and free disk space.
- Additional global transfer attributes on the Status sensor.
- Switch for qBittorrent alternative speed limits.
- Number entity for the global download limit (MB/s; `0` means unlimited).
- Local polling with configurable interval (15–300 seconds).
- No third-party Python dependency; credentials stay in the Home Assistant config entry.

## Installation with HACS

1. Open HACS → Integrations → ⋮ → **Custom repositories**.
2. Add `https://github.com/Liionboy/ha-qbittorrent` and choose **Integration**.
3. Install **qBittorrent**, restart Home Assistant, then add the integration from the UI.

## Requirements

- Home Assistant 2024.6 or newer.
- qBittorrent WebUI with API v2 enabled (qBittorrent 4.1+).
- The Home Assistant host must be able to reach the WebUI URL.

## Security

Use HTTPS when the WebUI is accessed through a reverse proxy. Do not expose qBittorrent's WebUI directly to the internet; prefer a VPN or authenticated reverse proxy.

## Development

```bash
python -m pytest -q
python -m compileall custom_components
```

## Credits

qBittorrent is a trademark of its respective project. This is an independent Home Assistant integration.
