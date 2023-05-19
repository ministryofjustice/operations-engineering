import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from python.config.logging_config import logging
from python.lib.moj_archive import MojArchive
from python.lib.moj_github import MojGithub

MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME = "ministryofjustice"
MINISTRYOFJUSTICE_REPOS_ALLOW_LIST = [
    "django-pagedown",
    "govuk-pay-ruby-client",
    "govuk_notify_rails",
    "analytics-platform-auth0",
    "pflr-express-kit",
    "hmpps-terraform-modules",
    "laa-nolasa",
    "hmpps-track-a-move",
    "notify-for-wordpress",
    "jwt-laminas-auth"
]
MINISTRYOFJUSTICE_REPOS_TYPE_TO_CHECK = "public"

MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME = "moj-analytical-services"
MOJ_ANALYTICAL_SERVICES_REPOS_ALLOW_LIST = [
    "timeliness_ctx",
    "GPC-anomalies",
    "pq-tool",
    "opg-data-processing",
    "df_criminal_court_research"
]
MOJ_ANALYTICAL_SERVICES_REPOS_TYPE_TO_CHECK = "all"


def get_commit(repository):
    # Try block needed as get_commits() can cause exception when
    # a repository has no commits as GH returns negative result.
    try:
        commits = repository.get_commits()
        return commits[0]
    except Exception:
        return 0


def ready_for_archiving(repository, archive_date) -> bool:
    commit = get_commit(repository)
    if commit == 0:
        logging.warning(f"Manually check repository: {repository.name}")
    elif commit.commit.author.date < archive_date:
        return True
    return False


def get_environment_variables() -> tuple[str, str]:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    github_organization_name = os.getenv("GITHUB_ORGANIZATION_NAME")
    if not github_organization_name:
        raise ValueError(
            "The env variable GITHUB_ORGANIZATION is empty or missing")

    return github_token, github_organization_name


def get_config_for_organization(github_organization_name: str) -> tuple[str, list[str], str] | ValueError:
    if github_organization_name == MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME:
        return MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME, MINISTRYOFJUSTICE_REPOS_ALLOW_LIST, MINISTRYOFJUSTICE_REPOS_TYPE_TO_CHECK

    if github_organization_name == MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME:
        return MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME, MOJ_ANALYTICAL_SERVICES_REPOS_ALLOW_LIST, MOJ_ANALYTICAL_SERVICES_REPOS_TYPE_TO_CHECK

    raise ValueError(
        f"Unsupported Github Organization Name [{github_organization_name}]")


def archive_inactive_repositories_by_date_and_type(github_token: str, organization_name: str, archive_date: datetime,
                                                   allow_list: list[str],
                                                   repo_type_to_archive: str):
    moj_gh = MojGithub(org=organization_name, org_token=github_token)

    repos = [
        repo
        for repo in moj_gh.get_unarchived_repos(repo_type_to_archive)
        if ready_for_archiving(repo, archive_date)
    ]

    logging.info(f"Beginning archive of inactive repositories for GitHub organization: {organization_name}")
    logging.info("-----------------------------")
    logging.info(f"Searching for inactive repositories from date: {archive_date}")
    logging.info("-----------------------------")

    for repo in repos:
        MojArchive(repo, allow_list).archive()


def main():
    github_token, github_organization_name = get_environment_variables()
    organization_name, allow_list, repo_type_to_archive = get_config_for_organization(github_organization_name)
    archive_date = datetime.now() - relativedelta(days=0, months=6, years=1)
    archive_inactive_repositories_by_date_and_type(github_token, organization_name, archive_date, allow_list,
                                                   repo_type_to_archive)


if __name__ == "__main__":
    main()
