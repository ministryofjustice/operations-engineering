local-setup:
	brew install pre-commit && pre-commit install

redact-terraform-output:
	sed -e 's/AWS_SECRET_ACCESS_KEY".*/<REDACTED>/g' \
		-e 's/AWS_ACCESS_KEY_ID".*/<REDACTED>/g' \
		-e 's/$AWS_SECRET_ACCESS_KEY".*/<REDACTED>/g' \
		-e 's/$AWS_ACCESS_KEY_ID".*/<REDACTED>/g' \
		-e 's/\[id=.*\]/\[id=<REDACTED>\]/g' \
		-e 's/::[0-9]\{12\}:/::REDACTED:/g' \
		-e 's/:[0-9]\{12\}:/:REDACTED:/g'
