import requests


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
