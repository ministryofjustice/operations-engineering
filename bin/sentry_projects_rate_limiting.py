import os
import json
import requests


def get_sentry_token():
    sentry_token = os.getenv("SENTRY_TOKEN")
    if not sentry_token:
        raise ValueError("The env variable SENTRY_TOKEN is empty or missing")

    return sentry_token


def get_org_teams(headers, base_url):
    org_teams_url = f"{base_url}/organizations/ministryofjustice/teams/"
    response = requests.get(org_teams_url, headers=headers, timeout=10)
    if response.status_code == 200:
        teams = json.loads(response.content)
        return teams
    return None


def get_project_keys(headers, base_url, project_slug):
    project_key_url = f"{base_url}/projects/ministryofjustice/{project_slug}/keys/"
    response = requests.get(project_key_url, headers=headers, timeout=10)
    if response.status_code == 200:
        project_keys = json.loads(response.content)
        return project_keys
    return None


def print_project_key_info(project_key):
    project_key_name = project_key["name"]
    rate_limit = project_key["rateLimit"]

    print(f"  Key Name: {project_key_name}")
    print(f"  Rate Limit: {rate_limit}")

    if rate_limit is None:
        print("  Rate Limited: True")
    else:
        print("  Rate Limited: False")

    if project_key["isActive"]:
        print("  Active: True")
    else:
        print("  Active: False")


def check_sentry_projects(headers, base_url, teams):
    if teams is not None:
        check_sentry_projects_teams(headers, base_url, teams)


def check_sentry_projects_teams(headers, base_url, teams):
    total_keys = 0
    rate_limited_keys = 0

    for team in teams:
        team_name = team["name"]
        print(f"Team: {team_name}")

        for project in team["projects"]:
            project_slug = project["slug"]
            project_name = project["name"]
            project_status = project["status"]

            print(f" Project: {project_name}")
            print(f" Status: {project_status}")

            project_keys = get_project_keys(
                headers, base_url, project_slug)

            if project_keys is not None:
                for project_key in project_keys:
                    total_keys += 1

                    print_project_key_info(project_key)

                    if project_key["rateLimit"] is None:
                        rate_limited_keys += 1

                    print("")

    print(f"Total Keys: {total_keys}")
    print(f"Rate Limited Keys: {(total_keys - rate_limited_keys)}")
    print(f"Non Rate Limited Keys: {rate_limited_keys}")


def main():
    print("Start \n")
    sentry_token = get_sentry_token()
    headers = {"Authorization": "Bearer " + sentry_token}
    base_url = "https://sentry.io/api/0"
    teams = get_org_teams(headers, base_url)
    check_sentry_projects(headers, base_url, teams)
    print("\n Finished")


if __name__ == "main":
    main()
