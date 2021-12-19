import logging
from typing import List, Tuple
import requests
from requests.api import head
from dataclasses import dataclass
from events import Events

_LOGGER = logging.getLogger(__name__)

GOVEE_API_URL = "https://developer-api.govee.com/v1/devices/"
HEADER_API_KEY = "Govee-API-Key"


@dataclass
class BloveeDevice:
    name: str
    model: str
    mac: str
    err: str
    is_online: bool


class Blovee:
    def __init__(self, api_key: str) -> None:
        self.events = Events()
        self._api_key = api_key
        self._devices = {}
        pass

    def get_devices(self) -> Tuple[List[BloveeDevice], str]:
        with requests.get(url=GOVEE_API_URL,
                          headers={HEADER_API_KEY: self._api_key}) as response:
            err = None
            if response.status_code == 200:
                for device in response.json()["data"]["devices"]:
                    device_id = device["device"]
                    if device_id in self._devices.keys():
                        # Device has already been added.
                        continue

                    # Create and add device to list
                    self._devices[device_id] = BloveeDevice(
                        name=device["deviceName"],
                        model=device["model"],
                        mac=device["device"])
                    self.events.new_device(self._devices[device_id])
            else:
                err = response.text()

        return self._devices, err

    def get_device_state(self, device: BloveeDevice) -> BloveeDevice:
        with requests.get(url=GOVEE_API_URL + "state",
                          headers={HEADER_API_KEY: self._api_key},
                          params={
                              device: device.mac,
                              "model": device.model
                          }) as response:
            if response.status_code == 200:
                for prop in response.json()["data"]["properties"]:
                    if "powerState" in prop:
                        device.is_online = prop["powerState"] == "on"
            else:
                device.err = response.text()

        return device

    def get_states(self) -> List[BloveeDevice]:
        _LOGGER.debug("get_states invoked")
        for device in self._devices:
            self._devices[device] = self.get_device_state(
                self._devices[device])

        return self._devices

    def turn_on(self, device: BloveeDevice):
        with requests.put(
                url=GOVEE_API_URL + "control/",
                headers={GOVEE_API_URL},
                json={
                    "device": device.mac,
                    "model": device.model,
                    "cmd": {
                        "name": "turn",
                        "value": "on"
                    },
                },
        ) as response:
            if response.status_code == 200:
                _LOGGER.debug("%s turned on", device.name)
            else:
                _LOGGER.error("Error turning on %s: %s", device.name,
                              response.text())
