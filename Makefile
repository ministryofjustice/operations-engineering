local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	# THis will only detect differences between staged changes and what's already beem committed locally
	pipenv run python -m local_jobs.generate_unit_tests --modified-files "$(shell git diff --cached --name-only | grep 'bin/\|services/' | xargs)"
