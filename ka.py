#!/usr/bin/env python3

from bluepy import btle
import time

COMMAND = bytes.fromhex("aa010000000000000000000000000000000000ab")


class Delegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        print("Initialized delegate")

    def handleNotification(self, cHandle, data):
        print("Received data %s:%s" % (cHandle, data))


two = btle.Peripheral("CB:31:30:30:35:0E", "random")
# dev = btle.Peripheral("D6:33:36:31:0F:64", "random")

two.setDelegate(Delegate())

while True:
    if two.waitForNotifications(1.0):
        print("handler should have been called")
        continue

    two.writeCharacteristic(handle=0x14, val=bytearray(COMMAND))
    print("Listening..")


# while True:
#     dev.writeCharacteristic(handle=0x14, val=bytearray(COMMAND))
#     time.sleep(1)
