#!/usr/bin/env python3
"""
Script to control Govee H6072 lamps. 

TODO: Add additonal commands.
"""

from binascii import hexlify
import time
import pygatt
from pygatt.backends.backend import BLEAddressType
import yaml
from actions import Actions
import argparse

RETRY_COUNT: int = 3

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, required=False, default="config.yaml")
parser.add_argument("action", type=Actions.from_string, choices=list(Actions))

args = parser.parse_args()

with open(args.config, "r") as stream:
    """
    Populate vars through yaml.
    """
    try:
        settings = yaml.safe_load(stream)
        addresses = settings["addresses"]
        service_id = settings["service_id"]
        characteristic_id = settings["characteristic_id"]
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


def handle_notif(handle, value):
    print("@ handle %d: Recevied: %s" % (handle, hexlify(value)))


def main(address: str, retry: int = 0):
    adapter = pygatt.GATTToolBackend()
    # TODO: Implement connection timeout handling.
    if retry >= RETRY_COUNT:
        print(
            "Connection to %s could not be established after %d tries."
            % (address, RETRY_COUNT)
        )
        exit(1)
    try:
        adapter.start()
        print("Connecting to %s" % address)
        device = adapter.connect(address_type=BLEAddressType.random, address=address)
        print("Connected to %s" % address)

        # device.char_write_handle(handle=0x14, value=args.action.get_bytes())
        # device.char_write(uuid=characteristic_id, value=args.action.get_bytes())

        # print("Reaading from handle")
        # print(device.char_read_handle(handle=0x10))
        # print("Reaading from UUID")
        # print(device.char_read(uuid="00010203-0405-0607-0809-0a0b0c0d2b10"))

        device.subscribe("00010203-0405-0607-0809-0a0b0c0d2b10", callback=handle_notif)

        while True:
            time.sleep(1)
            device.char_write_handle(handle=0x14, value=args.action.get_bytes())

        device.disconnect()
    except pygatt.exceptions.NotConnectedError:
        print("[%d] Connection error, trying again..." % (retry + 1))
        main(address, retry + 1)
    finally:
        adapter.stop()


for address in addresses:
    main(address=address)
