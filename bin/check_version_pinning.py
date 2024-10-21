import os

import yaml


def check_version_pinning(workflow_directory=".github/workflows"):
    # List to store the results
    results = []

    # Loop through all files in the specified workflow directory
    for root, _, files in os.walk(workflow_directory):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                file_path = os.path.join(root, file)

                # Open and parse the YAML file
                with open(file_path, "r") as f:
                    try:
                        workflows = yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        print(f"Error parsing {file_path}: {e}")
                        continue

                    # Check for `uses` fields
                    if workflows:
                        for job in workflows.get("jobs", {}).values():
                            for step in job.get("steps", []):
                                uses = step.get("uses", "")
                                if "@v" in uses and not (
                                    "actions/" in uses or "ministryofjustice" in uses
                                ):
                                    results.append(f"{file_path}: {uses}")

    # Report the results
    if results:
        print("Found workflows with pinned versions (@v):")
        for result in results:
            print(result)
    else:
        print("No workflows found with pinned versions (@v).")


if __name__ == "__main__":
    check_version_pinning()
