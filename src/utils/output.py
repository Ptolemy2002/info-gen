# A file for utility functions used by the uv script. You could put more utilities here as needed.
from datetime import datetime
import os
import warnings
from colorama import Fore

# Always show user warnings to the console
warnings.simplefilter('always', UserWarning)

# Make warnings print in one line
def warning_on_one_line(message, category, filename, lineno, file=None, line=None) -> str:
    return Fore.YELLOW + '%s: %s\n' % (category.__name__, message) + Fore.RESET

warnings.formatwarning = warning_on_one_line

def get_latest_main_outputs_dir() -> str:
    now: datetime = datetime.now()
    result: str = f"./src/outputs/main/{now.year}/{now.month:02d}/{now.day:02d}"

    # Find the folder representing the latest time with its name
    # Any errors happening here should be fatal, as it indicates the script
    # was not run properly (using the makefile)
    max_time: int = 0
    max_time_folder_name: str | None = None
    with os.scandir(result) as entries:
        for entry in entries:
            if entry.is_dir():
                # Convert HH-MM-SS to seconds
                split = entry.name.split("-")
                time = (int(split[0]) * 3600) + (int(split[1]) * 60) + int(split[2])
                if time >= max_time:
                    max_time = time
                    max_time_folder_name = entry.name

    if max_time_folder_name is not None:
        result = result + f"/{max_time_folder_name}"

    return result

def get_latest_outputs_dir(namespace: str) -> str:
    # Since the makefile only creates the outputs folder for the main namespace,
    # we create the outputs folder for other namespaces here.
    main_outputs_dir: str = get_latest_main_outputs_dir()
    if namespace == "main":
        return main_outputs_dir
    
    # For consistency, we will use the same timestamp as was used for main.
    # But here, we will create the folders ourselves instead of fatally erroring out
    # if they do not exist.
    result: str = main_outputs_dir.replace("/main/", f"/{namespace}/", 1)
    os.makedirs(result, exist_ok=True)
    return result

def get_manual() -> str:
    man = "No manual available."
    try:
        with open("./src/man.txt", "r") as f:
            man = f.read()
    except FileNotFoundError:
        # Just go with the default message
        pass

    return man