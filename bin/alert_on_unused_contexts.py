import os
import time

import yaml

from services.github_service import GithubService
from services.circleci_service import CircleciService


GITHUB_ORG = "ministryofjustice"


def yaml_convert(config):
    yaml_object = yaml.safe_load(config)
    return yaml_object


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
        print(f"Fetching pipelines for repo: {repo}")
        pipelines = circle_ci_service.get_circleci_pipelines_for_repository(repo)

        for pipeline in pipelines:
            all_pipeline_ids.append(pipeline["id"])

    return all_pipeline_ids


def main():
    slack_token, github_token, circleci_token = get_environment_variables()
    github_service = GithubService(github_token, GITHUB_ORG)
    circle_ci_service = CircleciService(circleci_token, os.getenv("CIRCLE_CI_OWNER_ID"), GITHUB_ORG)

    all_used_contexts = set()

    full_repository_list = github_service.get_org_repo_names()

    print("All repositories have been gathered.")

    full_pipeline_id_list = get_all_pipeline_ids_for_all_repositories(full_repository_list, circle_ci_service)

    print("All pipelines have been gathered.")

    try:
        for pipeline in full_pipeline_id_list:
            full_configuration_list = circle_ci_service.get_pipeline_configurations_from_pipeline_id(pipeline)
            if full_configuration_list:
                compiled_config = full_configuration_list.get("compiled", "")
                compiled_setup_config = full_configuration_list.get("compiled-setup-config", "")
                all_configurations_for_pipeline = [compiled_config, compiled_setup_config]
                for configuration in all_configurations_for_pipeline:
                    print("\n\n PEPPER - Configuration had been found!")
                    configuration_data = yaml.safe_load(configuration)
                    contexts_in_configuration = circle_ci_service.find_all_contexts_from_configuration(configuration_data)
                    all_used_contexts.update(contexts_in_configuration)

        all_contexts = circle_ci_service.list_all_contexts()
        unused_contexts = set(all_contexts) - all_used_contexts

        print("\n\n PEPPER - Unused context names:")
        for context in unused_contexts:
            print(f"Context name: {context}")
    except Exception as e:
        print(f"Error gathering contexts: {e}")


if __name__ == "__main__":
    main()
