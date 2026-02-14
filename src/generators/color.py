from typing import TypedDict, NotRequired
import random
from utils.colors import *
from utils.math import clamp

class ColorArgs(TypedDict):
    min_r: NotRequired[int]
    max_r: NotRequired[int]
    exact_r: NotRequired[int | None]
    min_g: NotRequired[int]
    max_g: NotRequired[int]
    exact_g: NotRequired[int | None]
    min_b: NotRequired[int]
    max_b: NotRequired[int]
    exact_b: NotRequired[int | None]

def gen_color(
        args: ColorArgs = {},
        log: bool = False
    ) -> str:
    """
        Generate a random color, represent it in Hex, RGB, and HSL formats, name the color, and return a formatted string with all this information.

        :param min_r: Minimum red value (0-255)
        :param max_r: Maximum red value (0-255)
        :param exact_r: If specified, use this exact red value instead of generating a random one.
        :param min_g: Minimum green value (0-255)
        :param max_g: Maximum green value (0-255)
        :param exact_g: If specified, use this exact green value instead of generating a random one.
        :param min_b: Minimum blue value (0-255)
        :param max_b: Maximum blue value (0-255)
        :param exact_b: If specified, use this exact blue value instead of generating a random one.
    """
    min_r = clamp(args.get('min_r', 0), 0, 255, log)
    max_r = clamp(args.get('max_r', 255), 0, 255, log)
    min_g = clamp(args.get('min_g', 0), 0, 255, log)
    max_g = clamp(args.get('max_g', 255), 0, 255, log)
    min_b = clamp(args.get('min_b', 0), 0, 255, log)
    max_b = clamp(args.get('max_b', 255), 0, 255, log)

    exact_r = args.get('exact_r')
    exact_g = args.get('exact_g')
    exact_b = args.get('exact_b')

    rgb: RGB = {
        'r': clamp(exact_r if exact_r is not None else random.randint(min_r, max_r), 0, 255, log),
        'g': clamp(exact_g if exact_g is not None else random.randint(min_g, max_g), 0, 255, log),
        'b': clamp(exact_b if exact_b is not None else random.randint(min_b, max_b), 0, 255, log)
    }

    hex: str = rgb_to_hex(rgb)
    hsl: HSL = rgb_to_hsl(rgb)
    cmyk: CMYK = rgb_to_cmyk(rgb)
    name: str = nearest_color(rgb)

    return f"{name} - rgb({rgb['r']}, {rgb['g']}, {rgb['b']}), hex: {hex}, hsl({hsl['h']:.2f}, {hsl['s']:.2f}%, {hsl['l']:.2f}%), cmyk({cmyk['c']:.2f}%, {cmyk['m']:.2f}%, {cmyk['y']:.2f}%, {cmyk['k']:.2f}%)"