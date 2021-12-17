from typing import Any
from homeassistant.components.light import DOMAIN, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import CONF_API_KEY
import requests
import logging


GOVEE_API_URL = "https://developer-api.govee.com/v1/devices/"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Setup Govee light platform"""
    request = requests.get(
        url=GOVEE_API_URL,
        headers={"Govee-API-Key": config[CONF_API_KEY]},
    )
    _LOGGER.debug(request.json())
    add_entities(
        GoveeH6072(d, config[CONF_API_KEY]) for d in request.json()["data"]["devices"]
    )


class GoveeH6072(LightEntity):
    """Govee H6072 Light."""

    def __init__(self, light, api) -> None:
        """Initialize H6072."""
        self._attr_unique_id = f'{light["device"]}_govee_light'
        self._mac = light["device"]
        self._name = light["deviceName"]
        self._model = light["model"]
        self._is_on = True
        self._attr_should_poll = False
        self._api = api
        self._attr_available = True
        self._attr_name = f"{self._name} Govee"
        _LOGGER.debug("Added %s" % self._attr_name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def mac(self) -> str:
        return self._mac

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._mac)},
            "name": self._name,
            "manufacturer": "Govee",
            "model": self._model,
            "via_device": (DOMAIN, "Govee API (cloud)"),
        }

    def update(self):
        self.fetch_state()

    def fetch_state(self):
        response = requests.get(
            url=GOVEE_API_URL + "state",
            params={"device": self._mac, "model": self._model},
            headers={"Govee-API-Key": self._api},
        )
        for prop in response.json()["data"]["properties"]:
            if "powerState" in prop:
                self._is_on = prop["powerState"] == "on"

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        response = requests.put(
            url=GOVEE_API_URL + "control/",
            headers={"Govee-API-Key": self._api},
            json={
                "device": self._mac,
                "model": self._model,
                "cmd": {"name": "turn", "value": "on"},
            },
        )
        if response.status_code == 200:
            self._is_on = True
        _LOGGER.debug("turned on")
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        response = requests.put(
            url=GOVEE_API_URL + "control/",
            headers={"Govee-API-Key": self._api},
            json={
                "device": self._mac,
                "model": self._model,
                "cmd": {"name": "turn", "value": "off"},
            },
        )
        if response.status_code == 200:
            self._is_on = False
        _LOGGER.debug("turned off")
        self.schedule_update_ha_state()
