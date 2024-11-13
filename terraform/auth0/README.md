# Auth0 Terraform Configuration

This README outlines the process of managing Auth0 resources using Terraform for the Operations Engineering team.

## Directory Structure

```text
.
├── operations-engineering/
│   ├── auth0_import.tf
│   ├── clients.tf
│   ├── main.tf
│   ├── tenant.tf
│   └── variables.tf
└── operations-engineering-test/
    ├── clients.tf
    ├── main.tf
    ├── tenant.tf
    └── variables.tf
```

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) (version 1.6.6 or compatible)
- Access to the Auth0 Management API
- AWS credentials for S3 backend access
- GitHub repository access

## Configuration

### Auth0 Provider

The Auth0 provider is configured using environment variables in the CI/CD pipeline:

- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`

These are sourced from GitHub secrets and set as Terraform variables in the workflow.

### Resource Configuration

Auth0 resources are defined in the respective `.tf` files. For example, clients are configured in `clients.tf`:

```hcl
resource "auth0_client" "prod_auth0managementapi" {
  name                = "Prod-Auth0ManagementAPI"
  app_type            = "non_interactive"
  is_first_party      = true
  oidc_conformant     = true
  grant_types         = ["client_credentials"]
  # ... (etc, etc...)
}
```

## Usage

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/ministryofjustice/operatiions-engineering.git
   cd operatiions-engineering/terraform/auth0
   ```

2. Set up your Auth0 credentials as environment variables:

   ```bash
   export AUTH0_DOMAIN="your_domain"
   export AUTH0_CLIENT_ID="your_client_id"
   export AUTH0_CLIENT_SECRET="your_client_secret"
   ```

3. Initialize Terraform:

   ```bash
   terraform init
   ```

4. Plan your changes:

   ```bash
   terraform plan
   ```

5. Apply changes:

Please run all apply operations through the CI/CD pipeline below.

### CI/CD Pipeline

The CI/CD pipeline is configured in `.github/workflows/cicd-terraform-auth0.yml`. It runs automatically on pull requests and pushes to the `main` branch that affect this directory.

The workflow performs the following steps:

1. Checkout code
2. Set up Terraform
3. Configure AWS credentials
4. Run Terraform fmt, init, validate, and plan
5. Post plan results as a comment on PRs
6. Apply changes when merged to main

## Security Considerations

- Credentials are stored as GitHub secrets and injected into the workflow as environment variables.
- AWS role assumption from Cloud Platform for S3 backend access.
- The Auth0 "Terraform Auth0 Provider" application in each tenant is used for authentication (client ID and secret)

## Troubleshooting

1. **Authentication Issues**:
   - Verify that the Auth0 credentials in GitHub secrets are correct and up-to-date.
   - Ensure the Auth0 application has the necessary permissions.

2. **Terraform State Conflicts**:
   - The state is stored in an S3 backend. Ensure you have the correct AWS permissions.

3. **Resource Creation Failures**:
   - Check the Auth0 logs for detailed error messages.
   - Verify that the Auth0 application has the required scopes.

## Links

- [Auth0 Terraform Provider Documentation](https://registry.terraform.io/providers/auth0/auth0/latest/docs)
- [Auth0 Management API Documentation](https://auth0.com/docs/api/management/v2)
- [Terraform Documentation](https://www.terraform.io/docs/index.html)
