# MicroPython USB macro Keypad
import logging
import asyncio
import gc
import aiorepl


from primitives.pushbutton import Pushbutton
from asyncio import Event

from typing import Any, List, Tuple
import usb.device
from usb.device.keyboard import KeyboardInterface, KeyCode, LEDCode
from machine import Pin
import time
import logging
import asyncio
import gc
import aiorepl


from translate import as_keychords
from config import layout

# Logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("kb")

def set_global_exception():
    def handle_exception(loop, context):
        import sys

        sys.print_exception(context["exception"])  # type: ignore
        sys.exit()

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)



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
            log.debug(f"Init pin {pin}")
            self.button = self.setup_button(pin)

        # Initialise all the LEDs as active-high outputs
        for pin, _ in leds:
            pin.init(Pin.OUT, value=0)

    def setup_button(self, button_pin:Pin):
        """Setup the button for async events"""
        # pin.init(Pin.IN, Pin.PULL_DOWN)
        button = Pushbutton(
            Pin(button_pin, Pin.IN, Pin.PULL_DOWN),
            # suppress=True,
        )
        # enable the event API for button press, double click, long press
        button.press_func(None)
        button.long_func(None)
        button.release_func(None)  # somehow needed to enable double click
        button.double_func(None)
        return button

    def run(self):
        # Old school synchronous loop
        while True:
            if self.is_open():

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
                                    self.send_keys([chord])
                                elif isinstance(chord, tuple):
                                    self.send_keys(chord)
                                else:
                                    # waited - avoid repeating the last key during long delays
                                    self.send_keys([])
                                    continue
                            # avoid repeating the last key after the end of the macro
                            self.send_keys([])
                        break

            else:
                print("Keyboard not open")

            # This simple example scans each input in an infinite loop, but a more
            # complex implementation would probably use a timer or similar.
            time.sleep_ms(1)

 
 
        # start the chair tasks based on the button events
        # return asyncio.gather(
        #     asyncio.create_task(self.handle_button_press(self.button.press)),
        #     # asyncio.create_task(self.handle_button_long(self.button.long)),
        #     # asyncio.create_task(self.handle_button_double(self.button.double)),
        #     # asyncio.create_task(self.handle_button_release(self.button.release)),
        #     # asyncio.create_task(self.do_stuff()),
        # )
    
    async def handle_button_press(self, event: Event):
        """Event received on a short button press,on doubleclick, and on a long press
        - Pressed > - Released
        - Pressed > - Double Click > - Released
        - Pressed > - Long Press > - Released
        """
        while True:
            if event:
                event.clear()
            await event.wait()
            if self.state == State.NORMAL:
                print("- Pressed")
                self.doe_ik_kies_jou()

# def run_keyboard():

#     # init the keyboard handler
#     hid_kb = PromptBoard(KEYS, LEDS)

#     # Register the keyboard interface and re-enumerate
#     usb.device.get().init(hid_kb, builtin_driver=True)

#     hid_kb.run()



# run_keyboard()



async def main():
    set_global_exception()  # Debug aid
    print("Starting tasks...")
    # Start other program tasks.
    asyncio.create_task(housekeeping())
    repl = asyncio.create_task(aiorepl.task())
    hid_kb = PromptBoard(KEYS, LEDS)

    # Register the keyboard interface and re-enumerate
    usb.device.get().init(hid_kb, builtin_driver=True)

    hid_kb.run()



    tasks = chair.run()
    await asyncio.gather(tasks, repl)


async def housekeeping():
    """Periodic housekeeping tasks."""
    while True:
        await asyncio.sleep(10)
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())


async def shutdown():
    print("Shutdown is running.")  # Happens in both cases
    await asyncio.sleep(1)
    print("done")


try:
    asyncio.run(main())
# except ZeroDivisionError:
#     asyncio.run(shutdown())
except KeyboardInterrupt:
    print("Keyboard interrupt at loop level.")
    asyncio.run(shutdown())
finally:
    asyncio.new_event_loop()  # Clear retained state