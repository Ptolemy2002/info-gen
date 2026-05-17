from typing import Any, Callable
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

def do_while(f: Callable[[], bool]) -> Callable[[], None]:
    """
        Annotation to turn a boolean function into a do-while loop.
        The function will be called at least once, and will continue to be called until it returns False.
    """
    def inner():
        while f():
            pass

    return inner