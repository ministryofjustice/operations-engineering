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


def get_repos_without_maintainers(github_service: GithubService):
    repos_without_maintainers = []

    for repository in github_service.fetch_all_repositories_in_org():
        repository_name = repository['node']['name']
        has_maintainer_collaborators = False
        has_maintainer_teams = False

        # Check for teams with maintain or admin permissions
        for team in github_service.get_repository_teams(repository_name):
            if team.permission in ['admin', 'maintain']:
                has_maintainer_teams = True
                break

        # Check for outside collaborators with maintain or admin permissions
        for collaborator in github_service.get_repository_collaborators(repository_name):
            if collaborator.permissions.admin == True or collaborator.permissions.maintain == True:
                has_maintainer_collaborators = True
                break

        if has_maintainer_teams == False and has_maintainer_collaborators == False:
            repos_without_maintainers.append(repository_name)

    if len(repos_without_maintainers) > 0:
        logger.warning("Repositories without any maintainers (team or individual):")
        for repository_name in repos_without_maintainers:
            logger.warning(repository_name)


def main():
    logging.info("Start")

    organisation_name, admin_github_token, slack_token = get_cli_arguments()
    slack_service = SlackService(slack_token)
    github_service = GithubService(admin_github_token, organisation_name)
    get_repos_without_maintainers(github_service)

    logging.info("Finished")

if __name__ == "__main__":
    main()
