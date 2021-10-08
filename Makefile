.PHONY: lint
lint:
	flake8 src
.PHONY: type-check
type-check:
	pytype src
.PHONY: ci
ci: lint type-check