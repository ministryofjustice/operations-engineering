#!/bin/sh

# For Repo
# terraform import -input=false -no-color module.REPO_NAME.github_repository.default REPO_NAME

# For secret
# terraform import -input=false -no-color 'module.REPO_NAME.github_actions_secret.default["SECRET_NAME"]' REPO_NAME/SECRET_NAME