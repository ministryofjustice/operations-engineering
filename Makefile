local-setup:
	brew install pre-commit && pre-commit install

generate-unit-tests:
	git fetch

	pipenv run python -m local_jobs.generate_unit_tests

	git diff main test/ai_test/test_bedrock_service.py
	git diff main:test/test_services/test_cloudtrail_service.py ./test/ai_test/test_cloudtrail_service.py
	git diff main:test/test_services/test_s3_service.py ./test/ai_test/test_s3_service.py
