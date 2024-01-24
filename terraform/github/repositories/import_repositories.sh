#tech-docs-github-pages-publisher
terraform import -input=false -no-color module.tech-docs-github-pages-publisher.github_repository.default tech-docs-github-pages-publisher
terraform import -input=false -no-color module.tech-docs-github-pages-publisher.github_branch_protection.default tech-docs-github-pages-publisher:main

terraform import -input=false -no-color 'module.tech-docs-github-pages-publisher.github_actions_secret.default["SLACK_WEBHOOK_URL"]' tech-docs-github-pages-publisher/SLACK_WEBHOOK_URL

#tech-docs-monitor
terraform import -input=false -no-color module.tech-docs-monitor.github_repository.default tech-docs-monitor
terraform import -input=false -no-color module.tech-docs-monitor.github_branch_protection.default tech-docs-monitor:main

terraform import -input=false -no-color 'module.tech-docs-monitor.github_actions_secret.default["SLACK_WEBHOOK_URL"]' tech-docs-monitor/SLACK_WEBHOOK_URL
terraform import -input=false -no-color 'module.tech-docs-monitor.github_actions_secret.default["REALLY_POST_TO_SLACK"]' tech-docs-monitor/REALLY_POST_TO_SLACK
terraform import -input=false -no-color 'module.tech-docs-monitor.github_actions_secret.default["SLACK_TOKEN"]' tech-docs-monitor/SLACK_TOKEN

#technical-guidance
terraform import -input=false -no-color module.technical-guidance.github_repository.default technical-guidance
terraform import -input=false -no-color module.technical-guidance.github_branch_protection.default technical-guidance:main

terraform import -input=false -no-color 'module.technical-guidance.github_actions_secret.default["SLACK_WEBHOOK_URL"]' technical-guidance/SLACK_WEBHOOK_URL
terraform import -input=false -no-color 'module.technical-guidance.github_actions_secret.default["GH_BOT_PAT_TOKEN"]' technical-guidance/GH_BOT_PAT_TOKEN
terraform import -input=false -no-color 'module.technical-guidance.github_actions_secret.default["OPERATIONS_ENGINEERING"]' technical-guidance/OPERATIONS_ENGINEERING
terraform import -input=false -no-color 'module.technical-guidance.github_actions_secret.default["OPS_BOT_TOKEN"]' technical-guidance/OPS_BOT_TOKEN

#template-documentation-site
terraform import -input=false -no-color module.template-documentation-site.github_repository.default template-documentation-site
terraform import -input=false -no-color module.template-documentation-site.github_branch_protection.default template-documentation-site:main

#template-repository
terraform import -input=false -no-color module.template-repository.github_repository.default template-repository
terraform import -input=false -no-color module.template-repository.github_branch_protection.default template-repository:main

#terraform-aws-mtasts
terraform import -input=false -no-color module.terraform-aws-mtasts.github_repository.default terraform-aws-mtasts
terraform import -input=false -no-color module.terraform-aws-mtasts.github_branch_protection.default terraform-aws-mtasts:main

#terraform-template-poc
terraform import -input=false -no-color module.terraform-template-poc.github_repository.default terraform-template-poc
terraform import -input=false -no-color module.terraform-template-poc.github_branch_protection.default terraform-template-poc:main

terraform import -input=false -no-color 'module.terraform-template-poc.github_actions_secret.default["AWS_STATE_ACCESS_KEY_ID"]' terraform-template-poc/AWS_STATE_ACCESS_KEY_ID
terraform import -input=false -no-color 'module.terraform-template-poc.github_actions_secret.default["AWS_STATE_SECRET_ACCESS_KEY"]' terraform-template-poc/AWS_STATE_SECRET_ACCESS_KEY
terraform import -input=false -no-color 'module.terraform-template-poc.github_actions_secret.default["GH_ACCESS_TOKEN"]' terraform-template-poc/GH_ACCESS_TOKEN


