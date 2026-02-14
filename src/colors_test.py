from utils.colors import *

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