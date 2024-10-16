# MicroPython USB macro Keypad

import logging
import time
from typing import Any,  List, NoReturn, Tuple

import usb.device
from machine import Pin
from read_config import update_prompts
from macro_kc import as_keychords
from usb.device.keyboard import KeyboardInterface,  LEDCode

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

prompt_bindings = {}


def show_key_state(keys=KEYS):
    for pin, code in keys:
        print(f"{pin} {pin.value()}")


class PromptBoard(KeyboardInterface):
    DEF_DELAY = -50
    debounce_ms = 30

    def __init__(self, keys: List[Tuple[Pin, Any]], leds):
        global prompt_bindings
        prompt_bindings = update_prompts(prompt_bindings, "/prompts.py")

        super().__init__()
        # Initialise all the pins as active-high inputs with pulldown resistors
        self.key_state = {}  # used to record the state of multi-step prompts

        for pin, id in keys:
            pin.init(Pin.IN, Pin.PULL_DOWN)
            log.debug(f"Init pin {pin}")
            self.key_state[id] = 0

        # Initialise all the LEDs as active-high outputs
        for pin, _ in leds:
            pin.init(Pin.OUT, value=0)

    def on_led_update(self, led_mask):
        print(hex(led_mask))
        for pin, code in LEDS:
            # Set the pin high if 'code' bit is set in led_mask
            pin(code & led_mask)

    def is_pressed(self, pin: Pin) -> bool:
        # basic debouncing
        if not pin.value():
            return False
        # wait for debounce
        time.sleep_ms(self.debounce_ms)
        # check if still high
        return pin.value() == 1

    def get_prompt(self, id):
        if not id:
            return ""
        if id not in prompt_bindings.keys():
            log.warning("No macro defined for this key")
            return ""

        if isinstance(prompt_bindings[id], str):
            # single prompt
            prompt = prompt_bindings[id]
        elif isinstance(prompt_bindings[id], list):
            # multi-step prompt, use key_state to track progress through the steps
            if self.key_state[id] < len(prompt_bindings[id]):
                prompt = prompt_bindings[id][self.key_state[id]]
                if not prompt.endswith(" ") or prompt.endswith("."):
                    prompt += " "
                self.key_state[id] += 1
            else:
                self.key_state[id] = 0
                prompt = ".\n"
        return prompt

    def send_prompt(self, prompt: str, delay: int = DEF_DELAY):
        macro_chords = as_keychords(prompt, delay)
        if macro_chords:
            for chord in macro_chords:
                if isinstance(chord, int):
                    self.send_keys([chord])
                elif isinstance(chord, tuple):
                    self.send_keys(chord)
                else:
                    # waited - avoid repeating the last key during long delays
                    self.send_keys([])
                    continue
            # avoid repeating the last key after the end of the macro
            self.send_keys([])

    def listen(self) -> NoReturn:
        global prompt_bindings

        counter = 0
        while True:
            if self.is_open():
                for pin, id in KEYS:
                    if self.is_pressed(pin):  # active-high
                        # Send Macro
                        prompt = self.get_prompt(id)
                        self.send_prompt(prompt)
                        break

            else:
                print("Keyboard not open")
            # This simple example scans each input in an infinite loop, but a more
            # complex implementation would probably use a timer or similar.
            time.sleep_ms(1)
            # Update the layout every 1000 iterations
            counter += 1
            if counter % 1000 == 0:
                prompt_bindings = update_prompts(prompt_bindings, "/config.py")
                counter = 0


def run_keyboard():

    # Register the keyboard interface and re-enumerate
    hid_kb = PromptBoard(KEYS, LEDS)
    usb.device.get().init(hid_kb, builtin_driver=True)
    log.info("Entering keyboard loop...")
    show_key_state()
    hid_kb.listen()


run_keyboard()
