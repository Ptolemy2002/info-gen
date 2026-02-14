from typing import TypedDict, NotRequired
from typo.vars import all_characters
import argparse
import re

def text_regex_type(s: str) -> str:
    re_groups = '|'.join([re.escape(c) for c in all_characters])
    if not re.fullmatch(fr'([{re_groups}]+)', s):
        raise argparse.ArgumentTypeError(f"Text must only contain the following characters or a space: {all_characters.strip()}")
    return s

def typo_weights_type(s: str) -> int:
    try:
        value = int(s)
        if value < 0:
            raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")
    
def rgb_bound_type(s: str) -> int:
    try:
        value = int(s)
        if not (0 <= value <= 255):
            raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")