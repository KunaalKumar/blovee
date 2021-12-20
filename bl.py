#!/usr/bin/env python3

from bluepy import btle
import time

# dev = btle.Peripheral("D6:33:36:31:0F:64", "random")
two = btle.Peripheral("CB:31:30:30:35:0E", "random")

# OFF
# COMMAND = bytes.fromhex("3301000000000000000000000000000000000032")
# ON
COMMAND = bytes.fromhex("3301010000000000000000000000000000000033")

# dev.writeCharacteristic(handle=0x14, val=bytearray(COMMAND))
two.writeCharacteristic(handle=0x14, val=bytearray(COMMAND))

# print("Services...")
# for s in dev.services:
#     print(s)
