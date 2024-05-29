import subprocess
import requests
import os
import json
import time

GITHUB_ORG = "ministryofjustice"
CIRCLECI_API_TOKEN = os.getenv("CIRCLECI_API_TOKEN")


def get_github_repos():
    return "cla-end-to-end-tests"


def get_circleci_pipelines(repo):
    url = f"https://circleci.com/api/v2/project/github/{GITHUB_ORG}/{repo}/pipeline"
    headers = {
        "Circle-Token": CIRCLECI_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting pipelines for {repo}: {response.text}")
        return []
    return response.json().get("items", [])


def get_pipeline_config(pipeline_id):
    url = f"https://circleci.com/api/v2/pipeline/{pipeline_id}/config"
    headers = {
        "Circle-Token": CIRCLECI_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting pipeline config {pipeline_id}: {response.text}")
        return {}
    return response.json()


def extract_contexts_from_config(config):
    yq_command = ['yq', 'e', '(.. | .context? | select(tag == "!!seq"))[], (.. | .context? | select(tag == "!!str"))']
    # yq e '(.. | .context? | select(tag == "!!seq"))[], (.. | .context? | select(tag == "!!str"))'
    result = subprocess.run(yq_command, input=config, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting contexts: {result.stderr}")
        return []
    return result.stdout.splitlines()


def list_all_contexts():
    url = "https://circleci.com/api/v2/context"
    headers = {
        "Circle-Token": CIRCLECI_API_TOKEN
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Whoopsie! Error listing contexts: {response.text}")
        return []
    contexts = response.json().get("items", [])
    return [context["name"] for context in contexts]


def main():
    repo = get_github_repos()
    # all_used_contexts = set()

    print(f"Processing repository: {repo}")
    pipelines = get_circleci_pipelines(repo)

    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        config = get_pipeline_config(pipeline_id)
        if config:
            compiled_config = config.get("compiled", "")
            compiled_setup_config = config.get("compiled-setup-config", "")
            all_configs = [compiled_config, compiled_setup_config]
            for cfg in all_configs:
                if cfg:
                    print(f'Config is this: {cfg}')
                    # contexts = extract_contexts_from_config(cfg)
                    # all_used_contexts.update(contexts)
        time.sleep(1)

    # all_contexts = list_all_contexts()
    # unused_contexts = set(all_contexts) - all_used_contexts

    # print("Unused contexts:")
    # for context in unused_contexts:
    #     print(context)


if __name__ == "__main__":
    main()
