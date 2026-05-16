from typing import Any
from argparse import ArgumentParser

def value_or_default(args: Any, key: Any, default: Any) -> Any:
    """Returns args[key] if it exists and is not None, otherwise default."""
    val = args.get(key)
    return val if val is not None else default

def arg_parser_has_arg(parser: ArgumentParser, arg: str) -> bool:
    """Returns True if the parser has an argument named arg."""
    for action in parser._actions:
        if arg in action.option_strings:
            return True
    return False