#!/bin/sh

#operations-engineering
terraform import -input=false -no-color module.operations-engineering.github_repository.default operations-engineering
terraform import -input=false -no-color module.operations-engineering.github_branch_protection.default operations-engineering:main

terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["ADMIN_GITHUB_TOKEN_ENTERPRISE_DATA"]' operations-engineering/ADMIN_GITHUB_TOKEN_ENTERPRISE_DATA
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["ADMIN_SEND_TO_SLACK"]' operations-engineering/ADMIN_SEND_TO_SLACK
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_CLIENT_ID"]' operations-engineering/AUTH0_CLIENT_ID
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_CLIENT_SECRET"]' operations-engineering/AUTH0_CLIENT_SECRET
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_DOMAIN"]' operations-engineering/AUTH0_DOMAIN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTID"]' operations-engineering/AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTID
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTSECRET"]' operations-engineering/AUTH0_OPERATIONS_ENGINEERING_DEV_DEFAULT_CLIENTSECRET
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTH0_OPERATIONS_ENGINEERING_DEV_DOMAIN"]' operations-engineering/AUTH0_OPERATIONS_ENGINEERING_DEV_DOMAIN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AUTO_REVIEW_DATE"]' operations-engineering/AUTO_REVIEW_DATE
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AWS_ID"]' operations-engineering/AWS_ID

terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["AWS_ID_DORMANT_USERS"]' operations-engineering/AWS_ID_DORMANT_USERS
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["CLOUD_PLATFORM_MOJ_GITHUB_TOKEN"]' operations-engineering/CLOUD_PLATFORM_MOJ_GITHUB_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["CODECOV_TOKEN"]' operations-engineering/CODECOV_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["GH_BOT_AUDIT_LOG_PAT_TOKEN"]' operations-engineering/GH_BOT_AUDIT_LOG_PAT_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["GH_BOT_PAT_TOKEN"]' operations-engineering/GH_BOT_PAT_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["KUBE_CERT"]' operations-engineering/KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["KUBE_CLUSTER"]' operations-engineering/KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["KUBE_NAMESPACE"]' operations-engineering/KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["KUBE_TOKEN"]' operations-engineering/KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["LOGGING_LEVEL"]' operations-engineering/LOGGING_LEVEL

terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["METADATA_API_TOKEN"]' operations-engineering/METADATA_API_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["METADATA_API_URL"]' operations-engineering/METADATA_API_URL
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["NOTIFY_PROD_API_KEY"]' operations-engineering/NOTIFY_PROD_API_KEY
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["NOTIFY_TEST_API_KEY"]' operations-engineering/NOTIFY_TEST_API_KEY
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["OPERATIONS_ENGINEERING"]' operations-engineering/OPERATIONS_ENGINEERING
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["OPS_BOT_TOKEN"]' operations-engineering/OPS_BOT_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["REPORTS_API_KEY"]' operations-engineering/REPORTS_API_KEY
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["ROUTE53_HOSTEDZONE_ID_1"]' operations-engineering/ROUTE53_HOSTEDZONE_ID_1
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["ROUTE53_HOSTEDZONE_ID_2"]' operations-engineering/ROUTE53_HOSTEDZONE_ID_2
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["S3_BUCKET_NAME"]' operations-engineering/S3_BUCKET_NAME

terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["SENTRY_TOKEN"]' operations-engineering/SENTRY_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["SLACK_BOT_TOKEN"]' operations-engineering/SLACK_BOT_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["SLACK_WEBHOOK_URL"]' operations-engineering/SLACK_WEBHOOK_URL
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["SONAR_TOKEN"]' operations-engineering/SONAR_TOKEN
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["TERRAFORM_ADMIN_DEV_LEVG"]' operations-engineering/TERRAFORM_ADMIN_DEV_LEVG
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["TERRAFORM_AUTH0_S3_ROLE_ARN_DEV"]' operations-engineering/TERRAFORM_AUTH0_S3_ROLE_ARN_DEV
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_DEV"]' operations-engineering/TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_DEV
terraform import -input=false -no-color 'module.operations-engineering.github_actions_secret.default["TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_PROD"]' operations-engineering/TERRAFORM_GITHUB_REPOS_S3_ROLE_ARN_PROD

#operations-engineering-certificate-renewal
terraform import -input=false -no-color module.operations-engineering-certificate-renewal.github_repository.default operations-engineering-certificate-renewal
terraform import -input=false -no-color module.operations-engineering-certificate-renewal.github_branch_protection.default operations-engineering-certificate-renewal:main

terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["AWS_ID"]' operations-engineering-certificate-renewal/AWS_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["EXPIRE_TEMPLATE_ID"]' operations-engineering-certificate-renewal/EXPIRE_TEMPLATE_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["GANDI_API_KEY"]' operations-engineering-certificate-renewal/GANDI_API_KEY
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["GANDI_ORG_ID"]' operations-engineering-certificate-renewal/GANDI_ORG_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["NOTIFY_API_KEY"]' operations-engineering-certificate-renewal/NOTIFY_API_KEY
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["REPORT_TEMPLATE_ID"]' operations-engineering-certificate-renewal/REPORT_TEMPLATE_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["REQUEST_GANDI_FUNDS_REPORT_TEMPLATE_ID"]' operations-engineering-certificate-renewal/REQUEST_GANDI_FUNDS_REPORT_TEMPLATE_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["REQUEST_GANDI_FUNDS_TEMPLATE_ID"]' operations-engineering-certificate-renewal/REQUEST_GANDI_FUNDS_TEMPLATE_ID
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["S3_BUCKET_NAME"]' operations-engineering-certificate-renewal/S3_BUCKET_NAME
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["S3_OBJECT_NAME"]' operations-engineering-certificate-renewal/S3_OBJECT_NAME

terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["SLACK_WEBHOOK_URL"]' operations-engineering-certificate-renewal/SLACK_WEBHOOK_URL
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["SONAR_TOKEN"]' operations-engineering-certificate-renewal/SONAR_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-certificate-renewal.github_actions_secret.default["UNDELIVERED_REPORT_TEMPLATE_ID"]' operations-engineering-certificate-renewal/UNDELIVERED_REPORT_TEMPLATE_ID

#operations-engineering-documentation-browser-extension
terraform import -input=false -no-color module.operations-engineering-documentation-browser-extension.github_repository.default operations-engineering-documentation-browser-extension
terraform import -input=false -no-color module.operations-engineering-documentation-browser-extension.github_branch_protection.default operations-engineering-documentation-browser-extension:main

#operations-engineering-example
terraform import -input=false -no-color module.operations-engineering-example.github_repository.default operations-engineering-example
terraform import -input=false -no-color module.operations-engineering-example.github_branch_protection.default operations-engineering-example:main

terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["DEVELOPMENT_ECR_ROLE_TO_ASSUME"]' operations-engineering-example/DEVELOPMENT_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["DEV_KUBE_CLUSTER"]' operations-engineering-example/DEV_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["DEV_KUBE_CERT"]' operations-engineering-example/DEV_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["DEV_KUBE_NAMESPACE"]' operations-engineering-example/DEV_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["DEV_KUBE_TOKEN"]' operations-engineering-example/DEV_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["PRODUCTION_ECR_ROLE_TO_ASSUME"]' operations-engineering-example/PRODUCTION_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["PROD_KUBE_CERT"]' operations-engineering-example/PROD_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["PROD_KUBE_CLUSTER"]' operations-engineering-example/PROD_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["PROD_KUBE_NAMESPACE"]' operations-engineering-example/PROD_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_secret.default["PROD_KUBE_TOKEN"]' operations-engineering-example/PROD_KUBE_TOKEN

#operations-engineering-join-github
terraform import -input=false -no-color module.operations-engineering-join-github.github_repository.default operations-engineering-join-github
terraform import -input=false -no-color module.operations-engineering-join-github.github_branch_protection.default operations-engineering-join-github:main

terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_KUBE_CERT"]' operations-engineering-join-github/DEV_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_KUBE_NAMESPACE"]' operations-engineering-join-github/DEV_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_KUBE_TOKEN"]' operations-engineering-join-github/DEV_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_CERT"]' operations-engineering-join-github/PROD_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_NAMESPACE"]' operations-engineering-join-github/PROD_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_TOKEN "]' operations-engineering-join-github/PROD_KUBE_TOKEN 
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["AUTH0_CLIENT_ID"]' operations-engineering-join-github/AUTH0_CLIENT_ID
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["AUTH0_CLIENT_SECRET"]' operations-engineering-join-github/AUTH0_CLIENT_SECRET
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_ADMIN_GITHUB_TOKEN"]' operations-engineering-join-github/DEV_ADMIN_GITHUB_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_ECR_ROLE_TO_ASSUME"]' operations-engineering-join-github/DEV_ECR_ROLE_TO_ASSUME

terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["DEV_FLASK_APP_SECRET"]' operations-engineering-join-github/DEV_FLASK_APP_SECRET
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["FLASK_APP_SECRET"]' operations-engineering-join-github/FLASK_APP_SECRET
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["KUBE_CLUSTER"]' operations-engineering-join-github/KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_CERT"]' operations-engineering-join-github/PROD_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_NAMESPACE"]' operations-engineering-join-github/PROD_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_KUBE_TOKEN"]' operations-engineering-join-github/PROD_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_ADMIN_GITHUB_TOKEN"]' operations-engineering-join-github/PROD_ADMIN_GITHUB_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_ECR_ROLE_TO_ASSUME"]' operations-engineering-join-github/PROD_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_secret.default["PROD_FLASK_APP_SECRET"]' operations-engineering-join-github/PROD_FLASK_APP_SECRET

#operations-engineering-metadata-poc
terraform import -input=false -no-color module.operations-engineering-metadata-poc.github_repository.default operations-engineering-metadata-poc
terraform import -input=false -no-color module.operations-engineering-metadata-poc.github_branch_protection.default operations-engineering-metadata-poc:main

terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_secret.default["DEVELOPMENT_ECR_ROLE_TO_ASSUME"]' operations-engineering-metadata-poc/DEVELOPMENT_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_secret.default["DEV_KUBE_CLUSTER"]' operations-engineering-metadata-poc/DEV_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_secret.default["DEV_KUBE_CERT"]' operations-engineering-metadata-poc/DEV_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_secret.default["DEV_KUBE_NAMESPACE"]' operations-engineering-metadata-poc/DEV_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_secret.default["DEV_KUBE_TOKEN"]' operations-engineering-metadata-poc/DEV_KUBE_TOKEN

#operations-engineering-reports
terraform import -input=false -no-color module.operations-engineering-reports.github_repository.default operations-engineering-reports
terraform import -input=false -no-color module.operations-engineering-reports.github_branch_protection.default operations-engineering-reports:main

terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["AUTH0_CLIENT_ID"]' operations-engineering-reports/AUTH0_CLIENT_ID
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["AUTH0_CLIENT_SECRET"]' operations-engineering-reports/AUTH0_CLIENT_SECRET
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["SLACK_WEBHOOK_URL"]' operations-engineering-reports/SLACK_WEBHOOK_URL
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEVELOPMENT_ECR_ROLE_TO_ASSUME"]' operations-engineering-reports/DEVELOPMENT_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_KUBE_CLUSTER"]' operations-engineering-reports/DEV_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_KUBE_CERT"]' operations-engineering-reports/DEV_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_KUBE_NAMESPACE"]' operations-engineering-reports/DEV_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_KUBE_TOKEN"]' operations-engineering-reports/DEV_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PRODUCTION_ECR_ROLE_TO_ASSUME"]' operations-engineering-reports/PRODUCTION_ECR_ROLE_TO_ASSUME
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_KUBE_CERT"]' operations-engineering-reports/PROD_KUBE_CERT

terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_KUBE_CLUSTER"]' operations-engineering-reports/PROD_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_KUBE_NAMESPACE"]' operations-engineering-reports/PROD_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_KUBE_TOKEN"]' operations-engineering-reports/PROD_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["KUBE_CERT"]' operations-engineering-reports/PROD_KUBE_CERT
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["KUBE_CLUSTER"]' operations-engineering-reports/PROD_KUBE_CLUSTER
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["KUBE_NAMESPACE"]' operations-engineering-reports/PROD_KUBE_NAMESPACE
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["KUBE_TOKEN"]' operations-engineering-reports/PROD_KUBE_TOKEN
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_FLASK_APP_SECRET"]' operations-engineering-reports/DEV_FLASK_APP_SECRET
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["FLASK_APP_SECRET"]' operations-engineering-reports/FLASK_APP_SECRET
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_FLASK_APP_SECRET"]' operations-engineering-reports/PROD_FLASK_APP_SECRET

terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["CVE_SCAN_SLACK_WEBHOOK"]' operations-engineering-reports/CVE_SCAN_SLACK_WEBHOOK
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["ECR_REGISTRY"]' operations-engineering-reports/ECR_REGISTRY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_OPERATIONS_ENGINEERING_REPORTS_API_KEY"]' operations-engineering-reports/DEV_OPERATIONS_ENGINEERING_REPORTS_API_KEY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["DEV_OPS_ENG_REPORTS_ENCRYPT_KEY"]' operations-engineering-reports/DEV_OPS_ENG_REPORTS_ENCRYPT_KEY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["OPERATIONS_ENGINEERING_REPORTS_API_KEY"]' operations-engineering-reports/OPERATIONS_ENGINEERING_REPORTS_API_KEY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["OPS_ENG_REPORTS_ENCRYPT_KEY"]' operations-engineering-reports/OPS_ENG_REPORTS_ENCRYPT_KEY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_OPERATIONS_ENGINEERING_REPORTS_API_KEY"]' operations-engineering-reports/PROD_OPERATIONS_ENGINEERING_REPORTS_API_KEY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_secret.default["PROD_OPS_ENG_REPORTS_ENCRYPT_KEY"]' operations-engineering-reports/PROD_OPS_ENG_REPORTS_ENCRYPT_KEY

#operations-engineering-runbooks
terraform import -input=false -no-color module.operations-engineering-runbooks.github_repository.default operations-engineering-runbooks
terraform import -input=false -no-color module.operations-engineering-runbooks.github_branch_protection.default operations-engineering-runbooks:main

terraform import -input=false -no-color 'module.operations-engineering-runbooks.github_actions_secret.default["GH_BOT_PAT_TOKEN"]' operations-engineering-runbooks/GH_BOT_PAT_TOKEN

#operations-engineering-terraform-github-repositories
terraform import -input=false -no-color module.operations-engineering-terraform-github-repositories.github_repository.default operations-engineering-terraform-github-repositories
terraform import -input=false -no-color module.operations-engineering-terraform-github-repositories.github_branch_protection.default operations-engineering-terraform-github-repositories:main

#operations-engineering-user-guide
terraform import -input=false -no-color module.operations-engineering-user-guide.github_repository.default operations-engineering-user-guide
terraform import -input=false -no-color module.operations-engineering-user-guide.github_branch_protection.default operations-engineering-user-guide:main

terraform import -input=false -no-color 'module.operations-engineering-user-guide.github_actions_secret.default["GH_BOT_PAT_TOKEN"]' operations-engineering-user-guide/GH_BOT_PAT_TOKEN


