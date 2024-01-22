#!/bin/sh

# For Repo
terraform import -input=false -no-color module.operations-engineering-devcontainer.github_repository.default operations-engineering-devcontainer

# For secret
# terraform import -input=false -no-color 'module.REPO_NAME.github_actions_secret.default["SECRET_NAME"]' REPO_NAME/SECRET_NAME