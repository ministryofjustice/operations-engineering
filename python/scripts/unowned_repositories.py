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
    repositories_without_maintainers = []
    repositories_with_no_associations = []
    repositories_without_admin_team = []
    repositories_without_any_admin = []
    repositories_without_any_teams = []
    allowed_teams = ["organisation-security-auditor", "all-org-members"]

    for repository in github_service.fetch_all_repositories_in_org():
        repository_name = repository['node']['name']
        has_maintainer_collaborator = False
        has_admin_collaborator = False
        has_maintainer_team = False
        has_admin_team = False
        repository_team_names = []
        repository_collaborators_count = 0
        repository_teams_count = 0

        # Check for teams with maintain or admin permissions
        repository_teams = github_service.get_repository_teams(repository_name)
        for team in repository_teams:
            repository_teams_count += 1
            repository_team_names.append(team.name)

            if team.permission == 'admin':
                has_maintainer_team = True
                has_admin_team = True
                break

            if team.permission == 'maintain':
                has_maintainer_team = True

        # Check for outside collaborators with maintain or admin permissions
        repository_collaborators = github_service.get_repository_collaborators(
            repository_name)
        for collaborator in repository_collaborators:
            repository_collaborators_count += 1

            if collaborator.permissions.admin == True:
                has_maintainer_collaborator = True
                has_admin_collaborator = True
                break

            if collaborator.permissions.maintain == True:
                has_maintainer_collaborator = True

        for allowed_team in allowed_teams:
            if repository_team_names.count(allowed_team) > 0:
                repository_team_names.remove(allowed_team)

        # Determine if repository has any permission problems via team and collaborators

        if has_maintainer_team == False and has_maintainer_collaborator == False:
            repositories_without_maintainers.append(repository_name)

        if repository_collaborators_count == 0 and repository_teams_count == 0:
            repositories_with_no_associations.append(repository_name)

        if has_admin_team == False:
            repositories_without_admin_team.append(repository_name)

        if has_admin_team == False and has_admin_collaborator == False:
            repositories_without_any_admin.append(repository_name)

        if len(repository_team_names) == 0:
            repositories_without_any_teams.append(repository_name)

    # Print the repositories that have permission problems

    if len(repositories_without_maintainers) > 0:
        logging.warning(
            "Repositories without any maintainers (team or individual):")
        for repository_name in repositories_without_maintainers:
            logging.warning(repository_name)

    if len(repositories_with_no_associations) > 0:
        logging.warning("Repositories with no teams or users attached:")
        for repository_name in repositories_with_no_associations:
            logging.warning(repository_name)

    if len(repositories_without_admin_team) > 0:
        logging.warning("Repositories without an admin team:")
        for repository_name in repositories_without_admin_team:
            logging.warning(repository_name)

    if len(repositories_without_any_admin) > 0:
        logging.warning(
            "Repositories without any admin team or admin collaborator:")
        for repository_name in repositories_without_any_admin:
            logging.warning(repository_name)

    if len(repositories_without_any_teams) > 0:
        logging.warning(
            "Repositories without any teams (except the organisation-security-auditor and all-org-members teams):")
        for repository_name in repositories_without_any_teams:
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
