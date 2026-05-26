from typo.vars import all_characters
import argparse
import re

def text_regex_argtype(s: str) -> str:
    re_groups = '|'.join([re.escape(c) for c in all_characters])
    if not re.fullmatch(fr'([{re_groups}]+)', s):
        raise argparse.ArgumentTypeError(f"Text must only contain the following characters or a space: {all_characters.strip()}")
    return s

def typo_weights_argtype(s: str) -> int:
    try:
        value = int(s)
        if value < 0:
            raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Typo weights must be non-negative integers.")
    
def rgb_bound_argtype(s: str) -> int:
    try:
        value = int(s)
        if not (0 <= value <= 255):
            raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("RGB bounds must be integers between 0 and 255.")
    
def subdomain_count_argtype(s: str) -> int:
    try:
        value = int(s)
        if value <= 0:
            raise argparse.ArgumentTypeError("Subdomain count must be an integer greater than 0.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Subdomain count must be an integer greater than 0.")
    
def case_insensitive_choice_argtype(choices: list[str]):
    def validator(s: str) -> str:
        for choice in choices:
            if s.lower() == choice.lower():
                return choice
        raise argparse.ArgumentTypeError(f"Invalid choice '{s}'. Valid choices are: {', '.join(choices)}.")
    return validator

def number_precision_argtype(s: str) -> int:
    try:
        value = int(s)
        if value < 0:
            raise argparse.ArgumentTypeError("Precision must be a non-negative integer.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Precision must be a non-negative integer.")
    
def number_field_length_argtype(s: str) -> int:
    try:
        value = int(s)
        if value < 0:
            raise argparse.ArgumentTypeError("Field length must be a non-negative integer.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Field length must be a non-negative integer.")

def count_argtype(s: str) -> int:
    try:
        value = int(s)
        if value < 1:
            raise argparse.ArgumentTypeError("Count must be a positive integer.")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Count must be a positive integer.")
        
def full_name_argtype(s: str) -> str:
    if s.count(' ') < 1:
        raise argparse.ArgumentTypeError("Full name must contain at least a first name and a last name separated by space.")
    return s