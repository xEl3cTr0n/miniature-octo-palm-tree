.PHONY: test run

test:
	pytest

run:
	uvicorn claimlens.api.main:app --reload
