from typing import TypedDict

class TypoArgs(TypedDict):
    text: str
    typos: list[str]
    typo_weights: list[int]
    typo_rate: float
    typos_per_word: int