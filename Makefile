local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	cover-agent \
  		--source-file-path "bin/test_job.py" \
  		--test-file-path "test/bin/test_test_job.py" \
  		--code-coverage-report-path "coverage.xml" \
  		--test-command "pipenv run tests" \
		--test-command-dir "./" \
		--coverage-type "cobertura" \
		--desired-coverage 90 \
		--max-iterations 3
