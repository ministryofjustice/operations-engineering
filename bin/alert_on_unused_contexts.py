import os
import time

import yaml

from services.github_service import GithubService
from services.circleci_service import CircleciService


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


def main():
    slack_token, github_token, circleci_token = get_environment_variables()
    github_service = GithubService(github_token)
    circle_ci_service = CircleciService(circleci_token, os.getenv("CIRCLE_CI_OWNER_ID"), "ministryofjustice")

    all_used_contexts = set()

    full_repository_list = github_service.get_org_repo_names()

    for repo in full_repository_list:
        print(f"PEPPER - Fetching pipelines for repo: {repo}")
        pipelines = circle_ci_service.get_circleci_pipelines_for_repository(repo)

        for pipeline in pipelines:
            pipeline_id = pipeline["id"]
            configurations = circle_ci_service.get_pipeline_configurations_from_pipeline_id(pipeline_id)
            if configurations:
                compiled_config = configurations.get("compiled", "")
                print(f"\n PEPPER - Compiled config: {compiled_config} \n")
                compiled_setup_config = configurations.get("compiled-setup-config", "")
                print(f"\n PEPPER - Compiled setup config: {compiled_setup_config} \n")
                all_configs = [compiled_config, compiled_setup_config]
                for cfg in all_configs:
                    if cfg:
                        print("\n\n PEPPER - Configuration had been found!")
                        configuration_data = yaml.safe_load(cfg)
                        contexts = circle_ci_service.find_all_contexts_from_configuration(configuration_data)
                        print(f"PEPPER - Contexts: {contexts}")
                        all_used_contexts.update(contexts)
            time.sleep(1)

    print(f"\n\n PEPPER - All used contexts final list: {all_used_contexts} \n\n")

    all_contexts = circle_ci_service.list_all_contexts()

    print(f"\n\n PEPPER - Total used context list: {all_contexts} \n\n")

    unused_contexts = set(all_contexts) - all_used_contexts

    print("\n\n PEPPER - Unused contexts:")
    for context in unused_contexts:
        print(context)


if __name__ == "__main__":
    main()
