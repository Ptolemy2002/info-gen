from typing import TypedDict
from scipy.spatial import KDTree
from warnings import warn
import json
import random
import os
import requests
import sys
from utils.types import *

colors: dict[str, RGB] | None = None
colors_tuples: list[tuple[int, int, int]] | None = None

def clean_dirty_colors():
    # Get the current colors file, which is in the `assets` folder and is JSON.
    dirty_colors_path = "./src/assets/colors-dirty.json"
    dirty_colors: list[DirtyColor] = []

    if os.path.exists(dirty_colors_path):
        with open(dirty_colors_path, "r") as f:
            data = json.load(f)
            dirty_colors = data.get("colors", [])
    else:
        # Fetch the colors from the API and save them to the dirty colors file.
        print(f"Dirty colors file not found at {dirty_colors_path}. Fetching from API endpoint https://api.color.pizza/v1/?list=default")
        response = requests.get("https://api.color.pizza/v1/?list=default")
        if response.status_code == 200:
            data = response.json()
            dirty_colors = data.get("colors", [])
            with open(dirty_colors_path, "w") as f:
                json.dump({"colors": dirty_colors}, f)
            print(f"Dirty colors fetched and saved to {dirty_colors_path}")
        else:
            warn(f"Failed to fetch colors from API. Status code: {response.status_code}. No colors will be available.")

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
    
    if not os.path.exists("./src/assets/colors.json"):
        warn("Colors file not found. Please run clean_dirty_colors() to fetch and clean the color data.")
        sys.exit(1)

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

def rgb_to_cmyk(rgb: RGB) -> CMYK:
    r = rgb["r"] / 255.0
    g = rgb["g"] / 255.0
    b = rgb["b"] / 255.0

    k = 1 - max(r, g, b)
    if k == 1:
        return {"c": 0, "m": 0, "y": 0, "k": 1}

    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

    return {"c": c * 100, "m": m * 100, "y": y * 100, "k": k * 100}

def cmyk_to_rgb(cmyk: CMYK) -> RGB:
    c = cmyk["c"] / 100.0
    m = cmyk["m"] / 100.0
    y = cmyk["y"] / 100.0
    k = cmyk["k"] / 100.0

    r = int(255 * (1 - c) * (1 - k))
    g = int(255 * (1 - m) * (1 - k))
    b = int(255 * (1 - y) * (1 - k))

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