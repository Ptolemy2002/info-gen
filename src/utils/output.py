# A file for utility functions used by the uv script. You could put more utilities here as needed.
import os
import warnings
from datetime import datetime
from typing import Callable
from colorama import Fore

# Always show user warnings to the console
warnings.simplefilter('always', UserWarning)

# Make warnings print in one line
def warning_on_one_line(message, category, filename, lineno, file=None, line=None) -> str:
    return Fore.YELLOW + '%s: %s\n' % (category.__name__, message) + Fore.RESET

warnings.formatwarning = warning_on_one_line

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _replace_last(string: str, old: str, new: str) -> str:
    old_idx = string.rfind(old)
    return string[:old_idx] + new + string[old_idx+len(old):]

def _time_key(name: str) -> int:
    h, m, s = name.split("-")
    return int(h) * 3600 + int(m) * 60 + int(s)


def _max_subdir(path: str, key_fn: Callable[[str], int]) -> str | None:
    max_key: int | None = None
    max_name: str | None = None
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                k = key_fn(entry.name)
                if max_key is None or k >= max_key:
                    max_key = k
                    max_name = entry.name
    return max_name


def get_latest_main_outputs_dir() -> str:
    path: str = os.path.join(SRC_DIR, "outputs/main")
    os.makedirs(path, exist_ok=True)
    
    for i, key_fn in enumerate([int, int, int, _time_key]):
        name = _max_subdir(path, key_fn)
        if name is None:
            # Create folders based on the current time if they do not exist.
            now = datetime.now()
            if i == 3: name = now.strftime("%H-%M-%S")
            elif i == 2: name = now.strftime("%d")
            elif i == 1: name = now.strftime("%m")
            else: name = now.strftime("%Y")
        
        path = os.path.join(path, name)
        os.makedirs(path, exist_ok=True)
    return path


def get_latest_outputs_dir(namespace: str) -> str:
    # Since the makefile only creates the outputs folder for the main namespace,
    # we create the outputs folder for other namespaces here.
    main_outputs_dir: str = get_latest_main_outputs_dir()
    if namespace == "main":
        return main_outputs_dir

    # For consistency, we will use the same timestamp as was used for main.
    # But here, we will create the folders ourselves instead of fatally erroring out
    # if they do not exist.
    result: str = _replace_last(main_outputs_dir, "/main/", f"/{namespace}/")
    os.makedirs(result, exist_ok=True)
    return result


def get_manual() -> str:
    man = "No manual available."
    try:
        with open(os.path.join(SRC_DIR, "man.txt"), "r") as f:
            man = f.read()
    except FileNotFoundError:
        # Just go with the default message
        pass

    return man