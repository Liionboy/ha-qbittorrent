"""Config flow for qBittorrent."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

from .api import QBittorrentApi, QBittorrentApiError
from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_URL, DOMAIN


async def _validate(hass: HomeAssistant, data: dict[str, str]) -> None:
    api = QBittorrentApi(
        async_get_clientsession(hass), data[CONF_URL], data[CONF_USERNAME], data[CONF_PASSWORD]
    )
    await api.async_login()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a qBittorrent setup flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            normalized = {**user_input, CONF_URL: user_input[CONF_URL].rstrip("/")}
            await self.async_set_unique_id(normalized[CONF_URL].lower())
            self._abort_if_unique_id_configured()
            try:
                await _validate(self.hass, normalized)
            except QBittorrentApiError as err:
                errors["base"] = "cannot_connect" if "connect" in str(err).lower() else "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=normalized[CONF_URL], data=normalized)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=DEFAULT_URL): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Return the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle qBittorrent options."""

    async def async_step_init(self, user_input: dict[str, int] | None = None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "scan_interval",
                        default=self.config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                    ): NumberSelector(NumberSelectorConfig(min=15, max=300, mode="box"))
                }
            ),
        )
