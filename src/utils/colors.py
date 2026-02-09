from typing import TypedDict
from scipy.spatial import KDTree
from warnings import warn
import json
import random

class RGB(TypedDict):
    r: int
    g: int
    b: int

class HSL(TypedDict):
    h: float
    s: float
    l: float

colors: dict[str, RGB] | None = None
colors_tuples: list[tuple[int, int, int]] | None = None

def clean_dirty_colors():
    # Get the current colors file, which is in the `assets` folder and is JSON.
    dirty_colors_path = "./src/assets/colors-dirty.json"
    dirty_colors = json.load(open(dirty_colors_path, "r"))["colors"]

    # Create a new list of colors with only the included keys.
    new_colors = []
    for color in dirty_colors:
        new_color = {}
        for key in ["name", "rgb"]:
            if key in color:
                new_color[key] = color[key]
            else:
                warn(f"Color {color} is missing key '{key}' and will be skipped.")
        new_colors.append(new_color)
    
    # Write the new colors to a new JSON file in the assets directory.
    new_colors_path = f"./src/assets/colors.json"
    with open(new_colors_path, "w") as f:
        json.dump({"colors": new_colors}, f)
    
    print(f"Clean colors file written to: {new_colors_path}")

def get_colors():
    global colors
    global colors_tuples

    if colors is not None:
        return colors
    
    colors = {}
    with open("./src/assets/colors.json", "r") as f:
        """
            We get the fololowing:
            {
                "colors": [
                    {
                        "name": "red",
                        "rgb": {
                            "r": 255,
                            "g": 0,
                            "b": 0
                        }
                    },
                    ...
            }
        """
        data = json.load(f)

    for color in data["colors"]:
        colors[color["name"]] = color["rgb"]
    
    colors_tuples = [(color["r"], color["g"], color["b"]) for color in colors.values()]
    
    return colors

def nearest_color(other_rgb: RGB) -> str:
    global colors_tuples

    colors = get_colors()
    names = list(colors.keys())

    tree = KDTree(colors_tuples)
    _, index = tree.query((other_rgb["r"], other_rgb["g"], other_rgb["b"]))
            
    return names[index]

def rgb_to_hex(rgb: RGB) -> str:
    return "#{:02x}{:02x}{:02x}".format(rgb["r"], rgb["g"], rgb["b"])

def hex_to_rgb(hex_color: str) -> RGB:
    hex_color = hex_color.lstrip("#")
    return {
        "r": int(hex_color[0:2], 16),
        "g": int(hex_color[2:4], 16),
        "b": int(hex_color[4:6], 16)
    }

def rgb_to_hsl(rgb: RGB) -> HSL:
    r = rgb["r"] / 255.0
    g = rgb["g"] / 255.0
    b = rgb["b"] / 255.0

    max_color = max(r, g, b)
    min_color = min(r, g, b)
    h = s = l = (max_color + min_color) / 2.0

    if max_color == min_color:
        h = s = 0  # achromatic
    else:
        d = max_color - min_color
        s = d / (1 - abs(2 * l - 1))
        if max_color == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_color == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return {"h": h * 360, "s": s * 100, "l": l * 100}

def hsl_to_rgb(hsl: HSL) -> RGB:
    h = hsl["h"] / 360.0
    s = hsl["s"] / 100.0
    l = hsl["l"] / 100.0

    if s == 0:
        r = g = b = int(l * 255)  # achromatic
    else:
        def hue_to_rgb(p: float, q: float, t: float) -> int:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return int(p + (q - p) * 6 * t)
            if t < 1/2:
                return int(q)
            if t < 2/3:
                return int(p + (q - p) * (2/3 - t) * 6)
            return int(p)

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return {"r": r, "g": g, "b": b}

if __name__ == "__main__":
    # Generate a random color and find the nearest color name
    random_color: RGB = {
        "r": random.randint(0, 255),
        "g": random.randint(0, 255),
        "b": random.randint(0, 255)
    }

    print(f"Random color: {random_color}")
    print(f"Hex: {rgb_to_hex(random_color)}")
    print(f"HSL: {rgb_to_hsl(random_color)}")

    print(f"Nearest color name: {nearest_color(random_color)}")