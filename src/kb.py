# MicroPython USB Keyboard example
#
# To run this example:
#
# 1. Check the KEYS assignment below, and connect buttons or switches to the
#    assigned GPIOs. You can change the entries as needed, look up the reference
#    for your board to see what pins are available. Note that the example uses
#    "active low" logic, so pressing a switch or button should switch the
#    connected pin to Ground (0V).
#
# 2. Make sure `usb-device-keyboard` is installed via: mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmpppppppppppppppmmmmmMMPPPPPPPPPPPPPPPPPPPP
#
# 3. Run the example via: mpremote run keyboard_example.py
#
# 4. mpremote will exit with an error after the previous step, because when the
#    example runs the existing USB device disconnects and then re-enumerates with
#   the keyboard interface present. At this point, the example is running.
#
# 5. The example doesn't print anything to the serial port, but to stop it first
#    re-connect: mpremote connect PORTNAME
#
# 6. Type Ctrl-C to interrupt the running example and stop it. You may have to
#    also type Ctrl-B to restore the interactive REPL.
#
# To implement a keyboard with different USB HID characteristics, copy the
# usb-device-keyboard/usb/device/keyboard.py file into your own project and modify
# KeyboardInterface.
#
# MIT license; Copyright (c) 2024 Angus Gratton
from typing import List, Tuple
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode, LEDCode
from machine import Pin
import time
import logging

from translate import text


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("kb")

# Tuples mapping Pin inputs to the KeyCode each input generates
#
# (Big keyboards usually multiplex multiple keys per input with a scan matrix,
# but this is a simple example.)
KEYS: List[Tuple[Pin, List[int]]] = [
    (Pin.cpu.GPIO28, [KeyCode.N1]),
    (Pin.cpu.GPIO2, [KeyCode.N2]),
    (Pin.cpu.GPIO5, [KeyCode.N3]),
    (Pin.cpu.GPIO27, [KeyCode.N4]),
    (Pin.cpu.GPIO11, [KeyCode.N5]),
    (Pin.cpu.GPIO7, [KeyCode.N6]),
    (Pin.cpu.GPIO19, [KeyCode.N7]),
    (Pin.cpu.GPIO17, [KeyCode.N8]),
    (Pin.cpu.GPIO14, [KeyCode.N9]),
    # ... add more pin to KeyCode mappings here if needed
]

# Tuples mapping Pin outputs to the LEDCode that turns the output on
LEDS = (
    (Pin.board.LED, LEDCode.CAPS_LOCK),
    # ... add more pin to LEDCode mappings here if needed
)

DEBUG = True


def show_key_state(keys=KEYS):
    for pin, code in keys:
        print(f"{pin} {pin.value()}")


class PromptBoard(KeyboardInterface):
    def on_led_update(self, led_mask):
        print(hex(led_mask))
        for pin, code in LEDS:
            # Set the pin high if 'code' bit is set in led_mask
            pin(code & led_mask)

    def __init__(self, keys, leds):
        super().__init__()
        # Initialise all the pins as active-high inputs with pulldown resistors
        for pin, _ in keys:
            log.debug(f"Init pin {pin}")
            pin.init(Pin.IN, Pin.PULL_DOWN)

        # Initialise all the LEDs as active-high outputs
        for pin, _ in leds:
            pin.init(Pin.OUT, value=0)


def run_keyboard():

    # Register the keyboard interface and re-enumerate
    hid_kb = PromptBoard(KEYS, LEDS)

    usb.device.get().init(hid_kb, builtin_driver=True)

    print("Entering keyboard loop...")

    keys = []  # Keys held down, reuse the same list object
    keys_down = [None]  # Previous keys, starts with a dummy value so first
    # iteration will always send
    show_key_state()

    while True:
        if hid_kb.is_open():
            keys.clear()
            for pin, code in KEYS:
                if pin.value():  # active-high
                    keys.append(code[0])
            if keys != keys_down:
                log.debug(keys)
                hid_kb.send_keys(keys)
                keys_down.clear()
                keys_down.extend(keys)
        else:
            print("Keyboard not open")

        # This simple example scans each input in an infinite loop, but a more
        # complex implementation would probably use a timer or similar.
        time.sleep_ms(1)


run_keyboard()
