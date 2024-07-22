local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	pipenv run python -m local_jobs.generate_unit_tests --modified-files "$(shell git diff --cached --name-only | grep 'bin/\|services/' | xargs)"
