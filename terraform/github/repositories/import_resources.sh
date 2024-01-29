#!/bin/sh
    
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["DEV_ECR_REGION"]' operations-engineering-join-github/DEV_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["DEV_ECR_REGISTRY"]' operations-engineering-join-github/DEV_ECR_REGISTRY
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["DEV_ECR_REPOSITORY"]' operations-engineering-join-github/DEV_ECR_REPOSITORY
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["PROD_ECR_REGION"]' operations-engineering-join-github/PROD_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["PROD_ECR_REGISTRY"]' operations-engineering-join-github/PROD_ECR_REGISTRY
terraform import -input=false -no-color 'module.operations-engineering-join-github.github_actions_variable.default["PROD_ECR_REPOSITORY"]' operations-engineering-join-github/PROD_ECR_REPOSITORY

terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_variable.default["ECR_REGISTRY"]' operations-engineering-reports/ECR_REGISTRY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_variable.default["DEVELOPMENT_ECR_REGION"]' operations-engineering-reports/DEVELOPMENT_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_variable.default["DEVELOPMENT_ECR_REPOSITORY"]' operations-engineering-reports/DEVELOPMENT_ECR_REPOSITORY
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_variable.default["PRODUCTION_ECR_REGION"]' operations-engineering-reports/PRODUCTION_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-reports.github_actions_variable.default["PRODUCTION_ECR_REPOSITORY"]' operations-engineering-reports/PRODUCTION_ECR_REPOSITORY

terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_variable.default["ECR_REGISTRY"]' operations-engineering-metadata-poc/ECR_REGISTRY
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_variable.default["DEVELOPMENT_ECR_REGION"]' operations-engineering-metadata-poc/DEVELOPMENT_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-metadata-poc.github_actions_variable.default["DEVELOPMENT_ECR_REPOSITORY"]' operations-engineering-metadata-poc/DEVELOPMENT_ECR_REPOSITORY

terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_variable.default["DEVELOPMENT_ECR_REPOSITORY"]' operations-engineering-example/DEVELOPMENT_ECR_REPOSITORY
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_variable.default["PRODUCTION_ECR_REGION"]' operations-engineering-example/PRODUCTION_ECR_REGION
terraform import -input=false -no-color 'module.operations-engineering-example.github_actions_variable.default["PRODUCTION_ECR_REPOSITORY"]' operations-engineering-example/PRODUCTION_ECR_REPOSITORY