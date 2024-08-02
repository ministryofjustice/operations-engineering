local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	git fetch

	pipenv run python -m local_jobs.generate_unit_tests
