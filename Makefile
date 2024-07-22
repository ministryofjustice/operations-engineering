local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	pipenv run python -m local_jobs.generate_unit_tests --modified-files "$(shell git diff --name-only main...$(shell git branch --show-current) | grep 'bin/\|services/' | xargs)"
