import os

from services.github_service import GithubService
from services.circleci_service import CircleciService
from services.slack_service import SlackService

# pylint: disable=W0718, R0914

GITHUB_ORG = "ministryofjustice"


def get_environment_variables() -> tuple:
    slack_token = os.getenv("ADMIN_SLACK_TOKEN")
    if not slack_token:
        raise ValueError(
            "The env variable ADMIN_SLACK_TOKEN is empty or missing")
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")
    circleci_token = os.getenv("ADMIN_CIRCLECI_TOKEN")
    if not circleci_token:
        raise ValueError(
            "The env variable ADMIN_CIRCLECI_TOKEN is empty or missing")
    circleci_owner_id = os.getenv("CIRCLE_CI_OWNER_ID")
    if not circleci_owner_id:
        raise ValueError(
            "The env variable CIRCLE_CI_OWNER_ID is empty or missing")

    return slack_token, github_token, circleci_token, circleci_owner_id


def main():
    slack_token, github_token, circleci_token, circleci_owner_id = get_environment_variables()
    github_service = GithubService(github_token, GITHUB_ORG)
    circle_ci_service = CircleciService(circleci_token, circleci_owner_id, GITHUB_ORG)
    slack_service = SlackService(slack_token)

    full_circle_ci_repository_list = github_service.check_circleci_config_in_repos()
    full_pipeline_id_list = circle_ci_service.get_all_pipeline_ids_for_all_repositories(full_circle_ci_repository_list)

    used_contexts = circle_ci_service.get_all_used_contexts(full_pipeline_id_list)

    all_contexts = circle_ci_service.list_all_contexts()

    unused_contexts = set(all_contexts) - used_contexts

    print("\n\n The following unused contexts have been found:")
    for context in unused_contexts:
        print(f"{context}")
    slack_service.send_unused_circleci_context_alert_to_operations_engineering(len(unused_contexts))


if __name__ == "__main__":
    main()
