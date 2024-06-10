import os
import yaml

from requests.exceptions import HTTPError, Timeout

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

    return slack_token, github_token, circleci_token


def get_all_pipeline_ids_for_all_repositories(repo_list, circle_ci_service):
    all_pipeline_ids = []

    for repo in repo_list:
        pipelines = circle_ci_service.get_circleci_pipelines_for_repository(repo)
        for pipeline in pipelines:
            all_pipeline_ids.append(pipeline["id"])

    return all_pipeline_ids


def main():
    slack_token, github_token, circleci_token = get_environment_variables()
    github_service = GithubService(github_token, GITHUB_ORG)
    circle_ci_service = CircleciService(circleci_token, os.getenv("CIRCLE_CI_OWNER_ID"), GITHUB_ORG)
    slack_service = SlackService(slack_token)

    all_used_contexts = set()

    full_circle_ci_repository_list = github_service.check_circleci_config_in_repos()
    full_pipeline_id_list = get_all_pipeline_ids_for_all_repositories(full_circle_ci_repository_list, circle_ci_service)

    try:
        for pipeline in full_pipeline_id_list:
            full_configuration_list = circle_ci_service.get_pipeline_configurations_from_pipeline_id(pipeline)
            if full_configuration_list:
                compiled_config = full_configuration_list.get("compiled", "")
                compiled_setup_config = full_configuration_list.get("compiled-setup-config", "")
                all_configurations_for_pipeline = [compiled_config, compiled_setup_config]
                for configuration in all_configurations_for_pipeline:
                    configuration_data = yaml.safe_load(configuration)
                    contexts_in_configuration = circle_ci_service.find_all_contexts_from_configuration(configuration_data)
                    all_used_contexts.update(contexts_in_configuration)

        all_contexts = circle_ci_service.list_all_contexts()
        unused_contexts = set(all_contexts) - all_used_contexts

        print("\n\n The following unused contexts have been found:")
        for context in unused_contexts:
            print(f"{context}")
        slack_service.send_unused_circleci_context_alert_to_operations_engineering(len(unused_contexts))

    except (HTTPError, Timeout) as e:
        print(f"Error gathering contexts due to network issues: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
