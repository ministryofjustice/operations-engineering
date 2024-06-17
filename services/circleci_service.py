import requests
import yaml


class CircleciService:
    def __init__(self, token, owner_id, github_org) -> None:
        self.github_org = github_org
        self.owner_id = owner_id
        self.base_url = "https://circleci.com/api/v2/"
        self.headers = {
          "Circle-Token": token
        }

    def get_circleci_pipelines_for_repository(self, repo):
        url = self.base_url + f"project/github/{self.github_org}/{repo}/pipeline"
        response = requests.get(url, headers=self.headers, timeout=60)
        if response.status_code != 200:
            print(f"Error getting pipelines for {repo}: {response.text}")
            return []
        pipelines = response.json().get("items", [])

        print(f"{len(pipelines)} pipelines found for repo: {repo}")
        return pipelines

    def get_pipeline_configurations_from_pipeline_id(self, pipeline_id):
        url = self.base_url + f"pipeline/{pipeline_id}/config"
        headers = self.headers
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f"Error getting pipeline config {pipeline_id}: {response.text}")
            return {}
        configurations = response.json()
        return configurations

    def find_all_contexts_from_configuration(self, configuration):
        contexts = []
        if isinstance(configuration, dict):
            for key, value in configuration.items():
                if key == "context":
                    if isinstance(value, list):
                        contexts.extend(value)
                    elif isinstance(value, str):
                        contexts.append(value)
                else:
                    contexts.extend(self.find_all_contexts_from_configuration(value))
        elif isinstance(configuration, list):
            for item in configuration:
                contexts.extend(self.find_all_contexts_from_configuration(item))

        return contexts

    def list_all_contexts(self):
        url = self.base_url + f"context?owner-id={self.owner_id}"
        headers = self.headers

        contexts = []
        next_page = None

        while True:
            response = requests.get(url, headers=headers, params={'page-token': next_page} if next_page else {}, timeout=360)
            if response.status_code != 200:
                print(f"Whoopsie! Error listing contexts: {response.text}")
                return []

            response_json = response.json()
            contexts.extend(context["name"] for context in response_json.get("items", []))
            next_page = response_json.get("next_page_token")

            if not next_page:
                break

        return contexts

    def get_all_pipeline_ids_for_all_repositories(self, repo_list):
        all_pipeline_ids = []

        for repo in repo_list:
            pipelines = self.get_circleci_pipelines_for_repository(repo)
            for pipeline in pipelines:
                all_pipeline_ids.append(pipeline["id"])

        return all_pipeline_ids

    def get_all_used_contexts(self, full_pipeline_id_list):
        all_used_contexts = set()

        for pipeline in full_pipeline_id_list:
            full_configuration_list = self.get_pipeline_configurations_from_pipeline_id(pipeline)
            if full_configuration_list:
                compiled_config = full_configuration_list.get("compiled", "")
                compiled_setup_config = full_configuration_list.get("compiled-setup-config", "")
                all_configurations_for_pipeline = [compiled_config, compiled_setup_config]
                for configuration in all_configurations_for_pipeline:
                    configuration_data = yaml.safe_load(configuration)
                    contexts_in_configuration = self.find_all_contexts_from_configuration(configuration_data)
                    all_used_contexts.update(contexts_in_configuration)

        return all_used_contexts
