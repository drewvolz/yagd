all: lint format usage

lint: mypy
check: lint

mypy:
	mypy --pretty --show-error-codes yagd/

format:
	./script/format

usage:
	python ./script/update-usage.py

.PHONY: mypy lint format usage check all
