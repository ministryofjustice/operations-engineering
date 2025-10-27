# Operations Engineering

[![Ministry of Justice Repository Compliance Badge](https://github-community.service.justice.gov.uk/repository-standards/api/operations-engineering/badge)](https://github-community.service.justice.gov.uk/repository-standards/operations-engineering)

This repository contains a collection of checks and reports developed and used by the Operations Engineering team at the Ministry of Justice.

## Our Vision

The Operations Engineering team buy, build, and run tools to help build and operate software at scale. While we primarily use the [Cloud Platform](https://user-guide.cloud-platform.service.justice.gov.uk/) for developing and hosting our services, our goal is to create tools and standards that can be used across multiple platforms and hosting services throughout the organisation.

## What's in This Repo

This mono repository includes code that performs various operations engineering tasks to streamline our workflow and maintain high operational standards. Here are some highlights:

- **Repository Reports:** We generate reports that verify the adherence of the Ministry of Justice organisation's repositories to the high standards outlined in our [Repository Standards](https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/). These reports help us maintain the quality of our code and streamline collaboration.

- **Sentry Monitoring:** We monitor Sentry for over and under-utilisation, ensuring we leverage this error-tracking tool to its full potential. This helps in identifying and rectifying application errors more efficiently.

- **Dormant User Detection:** Our code can detect inactive GitHub users and remove them from the organisation, keeping our workspace tidy and secure.

- **Github Repository Terraform:** Our Github repositories are defined in Terraform. How to create a new repository is outlined in a [Runbook](https://runbooks.operations-engineering.service.justice.gov.uk/documentation/services/github/repository-terraform.html).

These are just a few examples of this repository's useful tools and features. For more detailed information about each tool and feature and how they assist us in our operations, see the GitHub workflows in the `.github/workflows` directory for more information.

## Getting Started

1. **Clone the Repo:** `git clone https://github.com/ministryofjustice/operations-engineering.git`
2. **Install pre-commit:** `make local-setup`
3. **Navigate to the Repo:** `cd operations-engineering`
4. **Install Dependencies:** `pipenv install --dev`
5. **Run a script:** `pipenv run python -m bin.identify_dormant_github_users`

## Pipenv

### Basics

```bash
# Install pipenv via brew
brew install pipenv
# or via pip
python3 -m pip install pipenv

# Install all dependencies, including development dependencies
pipenv install --dev

# Run a script within the created virtual environment
pipenv run tests
# or as a command
pipenv run coverage run python -m unittest

# Get location of virtual environment (location may be needed to point your IDE to the right interpreter)
pipenv --venv

# Check for vulnerable packages
pipenv check

# Additional information on pipenv functionality
pipenv --help
```

## Naming Standards For Workflow Files

To aid navigation, standardisation and deprecation of workflows - we have opted to follow a simple naming convention for the different types of workflows that are contained within the repository.

For this, we use a prefix in the workflow filename - to ensure similar workflows are next to each other in most local development environments and an emoji in the workflow name - to ensure it's easily findable in the GitHub Actions UI.

Please ensure any new workflow files are prefixed with one of the below standards.

### `cicd-`

For any workflow that is purely related to Continuous Integration and Continuous Deployment, i.e. checks on PRs, deploying to environments etc.

Prefix the workflow name with: ♻️

### `job-`

For any workflow related to executing code that should be run periodically (whether automated or manual). This mainly relates to business processes that are automated to some degree.

If the job is completely automated (i.e. runs on a defined schedule), prefix the workflow name with: 🤖

If the job needs to be triggered manually, prefix the workflow name with: 🧑‍🔧

#### `experiment-`

For any workflow that is currently under testing, potentially for a proof-of-concept and isn't essential to any current process.

Prefix the workflow name with: 🧪

## Support

If you have any questions or need help with this repository, please contact us on the #ask-operations-engineering slack channel.

## License

This project is licensed under the [MIT License](/LICENSE.md).
