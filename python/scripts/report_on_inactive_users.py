import toml
import os

from python.services.github_service import GithubService

config_path = './python/config/inactive-users.toml'
config = toml.load(config_path)

ORGANISATION = config['github']['organisation_name']
INACTIVITY = config['activity_check']['inactivity_months']

def get_environment_variables() -> str:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token


def main():
    github_token = get_environment_variables()
    print(f"Running report on inactive users for {ORGANISATION}")
    teams = {k: v for k, v in config['team'].items()}  # Access 'team' sub-dictionary directly

    print(f"Teams: {teams}")

    print(GithubService(github_token, ORGANISATION).report_on_inactive_users(
        teams, INACTIVITY))


if __name__ == "__main__":
    main()

