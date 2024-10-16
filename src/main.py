import time
from machine import Pin
import asyncio
import aiorepl


STOP_BOOT_KEYS = [Pin.cpu.GPIO19, Pin.cpu.GPIO14]

# configure input pins with pull-down resistors
for pin in STOP_BOOT_KEYS:
    # log.debug("Init pin", pin)
    pin.init(Pin.IN, Pin.PULL_DOWN)


def stop_boot():
    if all(pin() for pin in STOP_BOOT_KEYS):
        return True

    return False


async def task1():
    while True:
        print("task 1")
        await asyncio.sleep_ms(500)
    print("done")


async def as_main():
    print("Starting tasks...")

    # Start other program tasks.
    t1 = asyncio.create_task(task1())

    # Start the aiorepl task.
    repl = asyncio.create_task(aiorepl.task())

    await asyncio.gather(t1, repl)


# import the keyboard example
if not stop_boot():
    asyncio.run(as_main())
