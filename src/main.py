import time
from machine import Pin


STOP_BOOT_KEYS = [Pin.cpu.GPIO19, Pin.cpu.GPIO14]

# configure input pins with pull-down resistors
for pin in STOP_BOOT_KEYS:
    # log.debug("Init pin", pin)
    pin.init(Pin.IN, Pin.PULL_DOWN)


def stop_boot():
    if all(pin() for pin in STOP_BOOT_KEYS):
        return True

    return False


# # wait 5 seconds before starting the keyboard example
# delay = 3
# for i in range(delay):
#     if stop_boot():
#         print("Exiting boot")
#         break

#     print("Starting keyboard example in %d seconds" % (delay - i))
#     time.sleep(1)

# import the keyboard example
if not stop_boot():
    from kb import *
    run_keyboard()

