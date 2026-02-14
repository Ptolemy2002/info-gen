from typing import TypedDict

class RGB(TypedDict):
    r: int
    g: int
    b: int

class HSL(TypedDict):
    h: float
    s: float
    l: float

class CMYK(TypedDict):
    c: float
    m: float
    y: float
    k: float

class DirtyColor(TypedDict):
    name: str
    rgb: RGB