from typing import TypedDict, NotRequired

class ColorArgs(TypedDict):
    min_r: NotRequired[int | None]
    max_r: NotRequired[int | None]
    exact_r: NotRequired[int | None]
    min_g: NotRequired[int | None]
    max_g: NotRequired[int | None]
    exact_g: NotRequired[int | None]
    min_b: NotRequired[int | None]
    max_b: NotRequired[int | None]
    exact_b: NotRequired[int | None]