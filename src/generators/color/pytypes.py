from typing import TypedDict, NotRequired

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