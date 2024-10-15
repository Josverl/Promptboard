# MicroPython USB macro Keypad

from typing import Any, List, Tuple
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode, LEDCode
from machine import Pin
import time
import logging

from translate import as_keychords
from config import layout

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("kb")

# Tuples mapping Pin inputs to the KeyCode each input generates
#
# (Big keyboards usually multiplex multiple keys per input with a scan matrix,
# but this is a simple example.)
KEYS: List[Tuple[Pin, str]] = [
    (Pin.cpu.GPIO28, "1"),
    (Pin.cpu.GPIO2, "2"),
    (Pin.cpu.GPIO5, "3"),
    (Pin.cpu.GPIO27, "4"),
    (Pin.cpu.GPIO11, "5"),
    (Pin.cpu.GPIO7, "6"),
    (Pin.cpu.GPIO19, "7"),
    (Pin.cpu.GPIO17, "8"),
    (Pin.cpu.GPIO14, "9"),
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

    def __init__(self, keys: List[Tuple[Pin, Any]], leds):
        super().__init__()
        # Initialise all the pins as active-high inputs with pulldown resistors
        for pin, _ in keys:
            pin.init(Pin.IN, Pin.PULL_DOWN)
            log.debug(f"Init pin {pin}")

        # Initialise all the LEDs as active-high outputs
        for pin, _ in leds:
            pin.init(Pin.OUT, value=0)


def run_keyboard():

    # Register the keyboard interface and re-enumerate
    hid_kb = PromptBoard(KEYS, LEDS)

    usb.device.get().init(hid_kb, builtin_driver=True)

    print("Entering keyboard loop...")

    show_key_state()

    while True:
        if hid_kb.is_open():

            # Send Macro

            for pin, code in KEYS:
                if pin.value():  # active-high
                    if not code:
                        continue
                    if not code in layout.keys():
                        print("No macro defined for this key")
                        continue
                    macro_codes = as_keychords(layout[code], -100)
                    if macro_codes:
                        for chord in macro_codes:
                            if isinstance(chord, int):
                                hid_kb.send_keys([chord])
                            elif isinstance(chord, tuple):
                                hid_kb.send_keys(chord)
                            else:
                                # waited - avoid repeating the last key during long delays
                                hid_kb.send_keys([])
                                continue
                        # avoid repeating the last key after the end of the macro
                        hid_kb.send_keys([])
                    break

        else:
            print("Keyboard not open")

        # This simple example scans each input in an infinite loop, but a more
        # complex implementation would probably use a timer or similar.
        time.sleep_ms(1)


run_keyboard()
