import sys
from python.config.logging_config import logging
from python.services.github_service import GithubService
from python.services.slack_service import SlackService


def get_cli_arguments() -> tuple[str, str, str] | ValueError:
    expected_number_of_parameters = 4
    if len(sys.argv) != expected_number_of_parameters:
        raise ValueError("Incorrect number of input parameters")

    organisation_name = sys.argv[1]
    admin_github_token = sys.argv[2]
    slack_token = sys.argv[3]
    return organisation_name, admin_github_token, slack_token


def check_the_repositories(github_service: GithubService):
    repositories_with_no_associations = []
    allowed_teams = ["organisation-security-auditor", "all-org-members"]

    for repository in github_service.fetch_all_repositories_in_org():
        repository_name = repository['node']['name']
        repository_has_collaborator = False
        repository_has_team = False

        # Check for teams and teams have users
        repository_teams = github_service.get_repository_teams(repository_name)
        for team in repository_teams:
            if team.members_count > 0 and team.name not in allowed_teams:
                repository_has_team = True

        # Check for outside collaborators
        repository_collaborators = github_service.get_repository_collaborators(
            repository_name)

        for collaborator in repository_collaborators:
            repository_has_collaborator = True

        # Determine if repository has no owners
        if repository_has_team == False and repository_has_collaborator == False:
            repositories_with_no_associations.append(repository_name)

    # Print the repositories that have owner problems

    if len(repositories_with_no_associations) > 0:
        logging.warning(
            "Repositories with no teams, teams with zero users or no users attached:")
        for repository_name in repositories_with_no_associations:
            logging.warning(repository_name)


def main():
    logging.info("Start")

    organisation_name, admin_github_token, slack_token = get_cli_arguments()
    slack_service = SlackService(slack_token)
    github_service = GithubService(admin_github_token, organisation_name)
    check_the_repositories(github_service)

    logging.info("Finished")


if __name__ == "__main__":
    main()
