.PHONY: dep-install uv-install rmzi rm-lock rm-outputs rm-pycache rm-venv reset lu-test typo-test colors-test start gen-ssn gen-phone gen-typos gen-ssns gen-phones gen-typos-multi clean-dirty-colors help make-help

DATE := $(shell date '+%Y/%m/%d')
TIME := $(shell date '+%H-%M-%S')

MAIN_OUTPUT_DIR = ./src/outputs/main/$(DATE)/$(TIME)
FULL_ARGS = $(ARGS)

dep-install:
	apt install colorized-logs moreutils -y

uv-install:
	curl -LsSf https://astral.sh/uv/install.sh | sh

rmzi:
	bash ./tools/rmzi.sh

rm-lock:
	rm -f ./uv.lock

rm-outputs:
	rm -rf ./src/outputs

rm-pycache:
	rm -rf __pycache__ **/__pycache__

rm-venv:
	rm -rf .venv

reset: rmzi rm-lock rm-outputs rm-pycache rm-venv

lu-test:
	uv run ./src/location_test.py

typo-test:
	uv run ./src/typo_test.py

colors-test:
	uv run ./src/colors_test.py

start:
	mkdir -p $(MAIN_OUTPUT_DIR) && \
	uv run ./src/main.py $(FULL_ARGS) 2>&1 | tee $(MAIN_OUTPUT_DIR)/log.txt
	(cat $(MAIN_OUTPUT_DIR)/log.txt | ansi2txt) | sponge $(MAIN_OUTPUT_DIR)/log.txt

gen-ssn: FULL_ARGS = ssn 1 -c $(ARGS)
gen-ssn: start

gen-phone: FULL_ARGS = phone 1 -c $(ARGS)
gen-phone: start

gen-address: FULL_ARGS = address 1 $(ARGS)
gen-address: start

gen-typos: FULL_ARGS = typos 1 $(ARGS)
gen-typos: start

gen-color: FULL_ARGS = color 1 $(ARGS)
gen-color: start

gen-ssns: FULL_ARGS = ssn $(ARGS)
gen-ssns: start

gen-phones: FULL_ARGS = phone $(ARGS)
gen-phones: start

gen-addresses: FULL_ARGS = address $(ARGS)
gen-addresses: start

gen-typos-multi: FULL_ARGS = typos $(ARGS)
gen-typos-multi: start

gen-colors: FULL_ARGS = color $(ARGS)
gen-colors: start

clean-dirty-colors: FULL_ARGS = --clean-dirty-colors $(ARGS)
clean-dirty-colors: start

help: FULL_ARGS = --help $(ARGS)
help: start

make-help:
	cat ./make-man.txt