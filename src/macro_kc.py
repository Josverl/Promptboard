"""
Translate text to keycodes for USB HID devices.
"""

# Based on : https://github.com/isoxliis/firmware-micropython/blob/main/isoxliis_macro.py
# Copyright (c) 2024 Jos Verlinde
# Copyright (c) 2024 isoxliis
# MIT License

import random
import time

from textwrap_dedent import dedent
from usb.device.keyboard import KeyCode as KC

a_to_z = range(ord("a"), ord("z") + 1)
one_to_nine = range(ord("1"), ord("9") + 1)

charmap = {
    # additional Common Keys
    9: KC.TAB,  # \t
    # 10: KC.ENTER
    10: (
        KC.LEFT_SHIFT,
        KC.ENTER,
    ),  # Shift-Enter gives LF without Sending(Enter) the prompt in Copilot
    32: KC.SPACE,
    33: (KC.LEFT_SHIFT, KC.N1),  # !
    34: (KC.LEFT_SHIFT, KC.QUOTE),  # "
    35: (KC.HASH),  # #
    36: (KC.LEFT_SHIFT, KC.N4),  # $
    37: (KC.LEFT_SHIFT, KC.N5),  # %
    38: (KC.LEFT_SHIFT, KC.N7),  # &
    39: (KC.QUOTE),  # '
    40: (KC.LEFT_SHIFT, KC.N9),  # (
    41: (KC.LEFT_SHIFT, KC.N0),  # )
    42: (KC.LEFT_SHIFT, KC.N8),  # *
    43: (KC.LEFT_SHIFT, KC.EQUAL),  # +
    44: KC.COMMA,  # ,
    45: KC.MINUS,  # -
    46: KC.DOT,  # .
    47: KC.SLASH,  # /
    58: (KC.LEFT_SHIFT, KC.COLON),
    59: KC.COLON,
    60: (KC.LEFT_SHIFT, KC.COMMA),  # <
    61: KC.EQUAL,
    62: (KC.LEFT_SHIFT, KC.DOT),  # >
    63: (KC.LEFT_SHIFT, KC.SLASH),  # ?
    64: (KC.LEFT_SHIFT, KC.N2),  # @,
    91: KC.OPEN_BRACKET,  # [
    92: KC.BACKSLASH,  # \
    93: KC.CLOSE_BRACKET,  # ]
    94: (KC.LEFT_SHIFT, KC.N6),  # ^
    95: (KC.LEFT_SHIFT, KC.MINUS),  # _
    123: (KC.LEFT_SHIFT, KC.OPEN_BRACKET),  # {
    124: (KC.LEFT_SHIFT, KC.BACKSLASH),  # |
    125: (KC.LEFT_SHIFT, KC.CLOSE_BRACKET),  # }
    126: (KC.LEFT_SHIFT, KC.TILDE),  # ` ~
    163: (KC.LEFT_SHIFT, KC.N3),  # £
}


DO_NOTHING = -1


def wait(delay: int):
    if delay == 0:
        return
    if delay < 0:
        delay = random.randint(5, -delay)

    t_until = time.ticks_ms() + delay

    while time.ticks_diff(t_until, time.ticks_ms()) > 0:
        time.sleep_ms(1)
        # yield DO_NOTHING


def hold(key, delay: int, auto_release=True):
    t_until = time.ticks_ms() + delay
    while time.ticks_diff(t_until, time.ticks_ms()) > 0:
        yield key
    if auto_release:
        yield 0


def repeat(key, times, delay: int = 0):
    for _ in range(times):
        yield key
        yield 0
        yield wait(delay)


def scancode(char: str):
    assert len(char) == 1, "scancode: Only single characters are supported"
    upper = char.isupper()
    char_ = ord(char.lower())
    if char_ in a_to_z:
        if upper:
            return KC.LEFT_SHIFT, char_ - 97 + KC.A
        else:
            return char_ - 97 + KC.A
    elif char_ in one_to_nine:
        return char_ - 49 + KC.N1
    elif char_ == 48:
        return KC.N0
    elif k := charmap.get(char_):
        return k
    else:
        return 0


def as_keychords(text: str, delay: int = -100):
    """
    Translate text to keycodes for USB HID devices.
    :param text: The text to translate.
    :param delay: The delay between each key press.

    :return: A generator that yields keycodes, tuples of keycodes.
    """
    assert isinstance(text, str), f"as_keychords: text must be a string not {type(text)}"

    # trim leading empty lines
    text = dedent(text.lstrip("\r\n"))

    # unindent text
    lines = text.split("\n")
    indent = len(lines[0]) - len(lines[0].lstrip())
    text = "\n".join(line[indent:] for line in lines)

    # delay = max(0, delay)
    last_key = None
    for char in text:
        sc = scancode(char)
        if isinstance(sc, tuple):
            mod, key = sc
            if key == last_key:
                yield 0
            last_key = key
            yield mod
            yield mod, key
        else:
            if sc == last_key:
                yield 0
            last_key = sc
            yield sc
        if delay:
            yield wait(delay)
