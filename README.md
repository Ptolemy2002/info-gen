# Information Generator
Generate personal information with either a guarantee or reasonable expectation that it does not conflict with real people.

## To Start
1. Ensure `uv` is installed. If not, run `make uv-install` to do so. Note that this does not automatically add the installation location to your `PATH`, so you must do that yourself.
2. In the root directory of the repository, execute the `make start ARGS="..."` command. `uv` will be invoked, creating a virtual environment, installing dependencies, and running the code in `main.py`.

## Requirements
**Minimum Python Version:** 3.13

**Python Dependencies:**
* `colorama` - for cross-platform colored terminal text.
* `us` - for finding realistic US locations.
* `uszipcode` - for generating realistic US zip codes.
* `sqlalchemy-mate<2.0.0.1` - for database interactions.
* `python-levenshtein` - for efficient string similarity calculations.
* `faker` - for generating fake addresses.
* `nltk` - for finding homophones of words, used in typo generation.
* `scipy` - for determining color distances

**Linux Dependencies:**
* `colorized-logs` - for removing ANSI color codes from log files.
* `moreutils` - for the `sponge` command used in log file processing.