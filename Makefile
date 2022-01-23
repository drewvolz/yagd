all: lint format

lint: mypy
check: lint

mypy:
	mypy --pretty --show-error-codes yagd/

format:
	./script/format

.PHONY: mypy lint format check all
