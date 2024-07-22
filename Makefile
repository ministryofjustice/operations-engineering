local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	pipenv run python -m local_jobs.generate_unit_tests \
  		--source-file-path "bin/test_job.py" \
  		--test-file-output-path "test/test_bin/test_test_job.py"
