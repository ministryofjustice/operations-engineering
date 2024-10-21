import os
import sys

import yaml


def find_workflow_files(workflow_directory=".github/workflows"):
    for root, _, files in os.walk(workflow_directory):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                yield os.path.join(root, file)


def parse_yaml_file(file_path):
    with open(file_path, "r", buffering=-1, encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing {file_path}: {e}")
            return None


def check_uses_field_in_workflow(workflows, file_path):
    results = []
    if workflows:
        for job in workflows.get("jobs", {}).values():
            for step in job.get("steps", []):
                uses = step.get("uses", "")
                if "@v" in uses and not (
                    "actions/" in uses or "ministryofjustice" in uses
                ):
                    results.append(f"{file_path}: {uses}")
    return results


def check_version_pinning(workflow_directory=".github/workflows"):
    all_results = []

    for file_path in find_workflow_files(workflow_directory):
        workflows = parse_yaml_file(file_path)
        if workflows:
            results = check_uses_field_in_workflow(workflows, file_path)
            all_results.extend(results)

    if all_results:
        print(
            "It may not be related to this PR, but the following third-party \
        GitHub Actions are using version pinning rather than commit has pinning."
        )
        print("The following workflows have incorrect pinned versions (@v):")
        for result in all_results:
            print(result)
        sys.exit(1)
    else:
        print("No workflows found with pinned versions (@v).")


if __name__ == "__main__":
    check_version_pinning()
