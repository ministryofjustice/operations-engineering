import os
import json
import requests


def main():
    sentry_token = os.getenv("SENTRY_TOKEN")
    if not sentry_token:
        raise ValueError(
            "The env variable SENTRY_TOKEN is empty or missing")

    print("Start \n")

    headers = {"Authorization": "Bearer " + sentry_token}
    base_url = "https://sentry.io/api/0"

    org_teams_url = f"{base_url}/organizations/ministryofjustice/teams/"
    response = requests.get(org_teams_url, headers=headers, timeout=10)

    if response.status_code == 200:
        rate_limited_keys = 0
        total_keys = 0

        teams = json.loads(response.content)

        for team in teams:
            team_name = team["name"]
            print(f"Team: {team_name}")

            for project in team["projects"]:
                project_slug = project["slug"]
                project_name = project["name"]
                project_status = project["status"]

                print(f" Project: {project_name}")
                print(f" Status: {project_status}")

                project_key_url = (
                    f"{base_url}/projects/ministryofjustice/{project_slug}/keys/"
                )
                response = requests.get(
                    project_key_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    project_keys = json.loads(response.content)

                    for project_key in project_keys:
                        total_keys += 1

                        project_key_name = project_key["name"]
                        rate_limit = project_key["rateLimit"]

                        print(f"  Key Name: {project_key_name}")
                        print(f"  Rate Limit: {rate_limit}")

                        if rate_limit is None:
                            rate_limited_keys += 1

                        if project_key["isActive"]:
                            print("  Active: True")
                        else:
                            print("  Active: False")
                        print("")

        print(f"Total Keys: {total_keys}")
        print(f"Rate Limited Keys: {(total_keys - rate_limited_keys)}")
        print(f"Non Rate Limited Keys: {rate_limited_keys}")

    print("\n Finished")


if __name__ == "__main__":
    main()
