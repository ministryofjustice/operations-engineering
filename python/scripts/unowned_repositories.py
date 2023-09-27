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


def get_org_teams(github_service: GithubService):
    org_teams = []
    ignore_teams = ["organisation-security-auditor", "all-org-members"]
    for team_name in github_service.get_team_names():
        if team_name in ignore_teams:
            continue
        team_repository_names = github_service.get_team_repository_names(
            team_name)
        team_user_names = github_service.get_team_user_names(team_name)
        org_teams.append(
            {
                "name": team_name,
                "repositories": team_repository_names,
                "number_of_users": len(team_user_names)
            }
        )
    return org_teams


def get_unowned_repositories(github_service: GithubService) -> list:
    repositories_with_no_associations = []
    org_teams = get_org_teams(github_service)

    for repository_name in github_service.get_org_repo_names():
        repository_has_team = False

        for team in org_teams:
            for team_repository_name in team["repositories"]:
                # Check repository has any team that has users in it
                if team_repository_name == repository_name and team["number_of_users"] > 0:
                    repository_has_team = True
                    break
            if repository_has_team == True:
                break

        if repository_has_team == False:
            # Check repository has any outside collaborators
            if len(github_service.get_repository_collaborators(repository_name)) == 0:
                # Repository has no owners
                repositories_with_no_associations.append(repository_name)

    # Print the repositories that have no owner
    if len(repositories_with_no_associations) > 0:
        logging.warning(
            "Repositories with no owners:")
        repositories_with_no_associations.sort()
        for repository_name in repositories_with_no_associations:
            logging.warning(repository_name)

    return repositories_with_no_associations


def send_slack_message(slack_service: SlackService, unowned_repositories: list):
    slack_service.send_unowned_repos_slack_message(unowned_repositories)


def main():
    logging.info("Start")

    organisation_name, admin_github_token, slack_token = get_cli_arguments()
    slack_service = SlackService(slack_token)
    github_service = GithubService(admin_github_token, organisation_name)
    unowned_repositories = get_unowned_repositories(github_service)
    if len(unowned_repositories) > 0:
        send_slack_message(slack_service, unowned_repositories)
    logging.info("Finished")


if __name__ == "__main__":
    main()
