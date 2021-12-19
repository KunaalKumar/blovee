import logging
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback

from blovee import Blovee

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def validate_api_key(hass: HomeAssistant, user_input):
    api_key = user_input[CONF_API_KEY]
    hub = Blovee(api_key)
    _, error = hub.get_devices()
    if error:
        raise CannotConnect(error)


@config_entries.HANDLERS.register(DOMAIN)
class BloveeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLe

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                await validate_api_key(self.hass, user_input)
            except CannotConnect as e:
                _LOGGER.exception("Cannot connect: %s", e)
                errors[CONF_API_KEY] = "cannot connect"
            except Exception as e:
                _LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(title=DOMAIN, data=user_input)

            return self.async_show_form(step_id="user", errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return BloveeOptionsFlowHandler(config_entry)


class BloveeOptionsFlowHandler(config_entries.OptionsFlow):
    VERSION = 1

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Manage the options."""
        # get the current value for API key for comparison and default value
        old_api_key = self.config_entry.options.get(
            CONF_API_KEY, self.config_entry.data.get(CONF_API_KEY, ""))

        errors = {}
        if user_input is not None:
            # check if API Key changed and is valid
            try:
                api_key = user_input[CONF_API_KEY]
                if old_api_key != api_key:
                    user_input = validate_api_key(self.hass, user_input)

            except CannotConnect as e:
                _LOGGER.exception("Cannot connect: %s", e)
                errors[CONF_API_KEY] = "cannot_connect"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"

            if not errors:
                # update options flow values
                self.options.update(user_input)
                return await self._update_options()
                # for later - extend with options you don't want in config but option flow
                # return await self.async_step_options_2()

        return self.async_show_form(
            step_id="user",
            errors=errors,
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title=DOMAIN, data=self.options)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
