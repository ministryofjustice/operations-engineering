import os

from services.github_service import GithubService

MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME = "ministryofjustice"
# Contains a base set of permissions for all users in MoJ
MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_BASE_TEAM_NAME = "all-org-members"

MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME = "moj-analytical-services"
# Contains a base set of permissions for all users in MoJAS
MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_BASE_TEAM_NAME = "everyone"


def get_environment_variables() -> tuple[str, str]:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    github_organization_name = os.getenv("GITHUB_ORGANIZATION_NAME")
    if not github_organization_name:
        raise ValueError(
            "The env variable GITHUB_ORGANIZATION is empty or missing")

    return github_token, github_organization_name


def get_config_for_organization(github_organization_name: str) -> tuple[str, str] | ValueError:
    if github_organization_name == MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME:
        return MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME, MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_BASE_TEAM_NAME

    if github_organization_name == MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME:
        return MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME, MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_BASE_TEAM_NAME

    raise ValueError(
        f"Unsupported Github Organization Name [{github_organization_name}]")


def main():
    github_token, github_organization_name = get_environment_variables()
    organization_name, organization_team_name = get_config_for_organization(
        github_organization_name)
    GithubService(github_token, organization_name).add_all_users_to_team(
        organization_team_name)


if __name__ == "__main__":
    main()
