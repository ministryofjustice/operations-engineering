#!/bin/sh

terraform import -input=false -no-color module.test-repository-levg.github_repository.default test-repository-levg
terraform import -input=false -no-color module.test-repository-levg2.github_repository.default test-repository-levg2