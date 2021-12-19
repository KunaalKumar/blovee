from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DELAY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.light import LightEntity

from .blovee import Blovee, BloveeDevice
from .const import CONF_USE_ASSUMED_STATE, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigType,
                            async_add_entities: AddEntitiesCallback):
    _LOGGER.debug("Setting up Blovee lights")
    config = entry.data
    options = entry.options
    hub = hass.data[DOMAIN]["hub"]

    update_interval = timedelta(
        seconds=options.get(CONF_DELAY, config.get(CONF_DELAY, 10)))

    hub.events.new_device += lambda device: async_add_entities()


class BloveeDataUpdateCoordinator(DataUpdateCoordinator):
    """Device state update handler."""
    def __init__(
        self,
        hass: HomeAssistant,
        logger,
        update_interval=None,
        *,
        config_entry: ConfigEntry,
    ):
        """Initialize global data updater."""
        self._config_entry = config_entry

        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=update_interval,
            update_method=self._async_update,
        )

    @property
    def use_assumed_state(self):
        """Use assumed states."""
        return self._config_entry.options.get(CONF_USE_ASSUMED_STATE, True)

    async def _async_update(self):
        """Fetch data."""
        self.logger.debug("_async_update")
        if DOMAIN not in self.hass.data:
            raise UpdateFailed("Blovee instance not available")
        hub: Blovee = self.hass.data[DOMAIN]["hub"]

        device_states = await hub.get_states()
        for device in device_states:
            if device.error:
                self.logger.warning("update failed for %s: %s", device.device,
                                    device.error)
        return device_states


class BloveeLightEntity(LightEntity):
    def __init__(self, hub: Blovee, title: str,
                 coordinator: BloveeDataUpdateCoordinator,
                 device: BloveeDevice):
        self._hub = hub
        self._title = title
        self._coordinator = coordinator
        self._device = device

    @property
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    # @property
    # def _state(self):
    #     """Lights internal state."""
    #     return self._device

    async def async_trun_on(self, **kwargs):
        """Turn on lamp."""
        _LOGGER.debug("async_turn_on for Blovee lamp %s, kwargs: %s",
                      self._device, kwargs)
        err = None
