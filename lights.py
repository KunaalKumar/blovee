#!/usr/bin/env python3
"""
Script to control Govee H6072 lamps. 

TODO: 1) Parse command line args for action.
      2) Allow specifying different config files (instead of just "config.yaml").
      3) Change address accept an array of addresses.
      4) ^ Handle multiple addresses.
      5) Add additonal commands.
"""

import asyncio
import pygatt
from pygatt.backends.backend import BLEAddressType
import yaml

OFF = bytearray(bytes.fromhex("3301000000000000000000000000000000000032"))
ON = bytearray(bytes.fromhex("3301010000000000000000000000000000000033"))

with open("config.yaml", "r") as stream:
    """ 
    Populate vars through yaml.
    """
    try:
        settings = yaml.safe_load(stream)
        address = settings["address"]
        service_id = settings["service_id"]
        characteristic_id = settings["characteristic_id"]
    except yaml.YAMLError as exc:
        print(exc)


async def main():
    adapter = pygatt.GATTToolBackend()
    # TODO: Implement connection timeout handling.
    try:
        adapter.start()
        print("Connecting..")
        device = adapter.connect(address_type=BLEAddressType.random,
                                 address=address)
        print("Connected!")
        device.char_write(uuid=characteristic_id, value=ON)
    finally:
        adapter.stop()


async def exec():
    await main()


asyncio.run(exec())
