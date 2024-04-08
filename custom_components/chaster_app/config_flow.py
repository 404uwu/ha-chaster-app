"""Config flow for chaster.app integration."""

from __future__ import annotations

import logging
from typing import Any

import requests
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CHASTER_API_BASEURL, CONF_API_TOKEN, CONF_LOCK_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_API_TOKEN): str, vol.Required(CONF_LOCK_ID): str}
)


class ChasterHub:
    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    def authenticate(self, lock_id: str, api_token: str) -> bool:
        """Test if we can authenticate with the host."""
        lock_details_response = requests.get(
            f"{CHASTER_API_BASEURL}/locks/{lock_id}",
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30,
        )
        if lock_details_response.status_code == 401:
            return False

        return lock_details_response.json()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    hub = ChasterHub(data[CONF_LOCK_ID])

    # connection_result = await hub.authenticate(data[CONF_LOCK_ID], data[CONF_API_TOKEN])
    connection_result = await hass.async_add_executor_job(
        hub.authenticate, data[CONF_LOCK_ID], data[CONF_API_TOKEN]
    )

    if connection_result is False:
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": connection_result["title"]}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for chaster.app."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self.async_set_unique_id(user_input[CONF_LOCK_ID])
                self._abort_if_unique_id_configured()

                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NotPermitted(HomeAssistantError):
    """Error to indicate the user is not permitted to execute an action."""
