# helper functions and tools to work with async functions
import asyncio

# ref: https://github.com/peterhinch/micropython-async/blob/master/v3/docs/TUTORIAL.md#224-a-typical-firmware-app



def set_global_exception():
    def handle_exception(loop, context):
        import sys

        sys.print_exception(context["exception"])  # type: ignore
        sys.exit()

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

