#!/bin/sh

terraform import -input=false -no-color module.acronyms.github_repository.default acronyms
terraform import -input=false -no-color 'module.acronyms.github_actions_secret.default["SLACK_WEBHOOK_URL"]' acronyms/SLACK_WEBHOOK_URL

terraform import -input=false -no-color module.cloud-platform-maintenance-pages.github_repository.default cloud-platform-maintenance-pages
terraform import -input=false -no-color 'module.cloud-platform-maintenance-pages.github_actions_secret.default["ECR_ROLE_TO_ASSUME"]' cloud-platform-maintenance-pages/ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.cloud-platform-maintenance-pages.github_actions_secret.default["KUBE_CERT"]' cloud-platform-maintenance-pages/KUBE_CERT
terraform import -input=false -no-color 'module.cloud-platform-maintenance-pages.github_actions_secret.default["KUBE_CLUSTER"]' cloud-platform-maintenance-pages/KUBE_CLUSTER
terraform import -input=false -no-color 'module.cloud-platform-maintenance-pages.github_actions_secret.default["KUBE_NAMESPACE"]' cloud-platform-maintenance-pages/KUBE_NAMESPACE
terraform import -input=false -no-color 'module.cloud-platform-maintenance-pages.github_actions_secret.default["KUBE_TOKEN"]' cloud-platform-maintenance-pages/KUBE_TOKEN

terraform import -input=false -no-color module.github-actions.github_repository.default github-actions

terraform import -input=false -no-color module.github-collaborators.github_repository.default github-collaborators
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["APP_ID"]' github-collaborators/APP_ID
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["APP_INSTALLATION_ID"]' github-collaborators/APP_INSTALLATION_ID
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["APP_PEM_FILE"]' github-collaborators/APP_PEM_FILE
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["AWS_ACCESS_KEY_ID"]' github-collaborators/AWS_ACCESS_KEY_ID
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["AWS_SECRET_ACCESS_KEY"]' github-collaborators/AWS_SECRET_ACCESS_KEY
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["NOTIFY_PROD_TOKEN"]' github-collaborators/NOTIFY_PROD_TOKEN
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["NOTIFY_TEST_TOKEN"]' github-collaborators/NOTIFY_TEST_TOKEN
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["OPS_BOT_TOKEN"]' github-collaborators/OPS_BOT_TOKEN
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["OPS_BOT_TOKEN_ENABLED"]' github-collaborators/OPS_BOT_TOKEN_ENABLED
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["POST_TO_GH"]' github-collaborators/POST_TO_GH
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["POST_TO_SLACK"]' github-collaborators/POST_TO_SLACK
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["SEND_TO_NOTIFY"]' github-collaborators/SEND_TO_NOTIFY
terraform import -input=false -no-color 'module.github-collaborators.github_actions_secret.default["SLACK_WEBHOOK_URL"]' github-collaborators/SLACK_WEBHOOK_URL

terraform import -input=false -no-color module.moj-terraform-aws-sso.github_repository.default moj-terraform-aws-sso

terraform import -input=false -no-color module.moj-terraform-scim-github.github_repository.default moj-terraform-scim-github