import json
import os

# from bin.print_github_repository_owners_repos import repositories
from services.github_service import GithubService


def get_environment_variables() -> tuple[str]:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError("The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    repository_limit = os.getenv("REPOSITORY_LIMIT") or 5

    return github_token, repository_limit


def convert_to_percentage(partial: int, total: int) -> str:
    return f"{round((partial / total) * 100)}%"


def contains_one_or_more(values: list[str], list_to_check: list[str]) -> bool:
    found = False

    for value in values:
        if value in list_to_check:
            found = True

    return found


def main():
    github_token, repository_limit = get_environment_variables()
    github_service = GithubService(github_token, "ministryofjustice")
    repositories = github_service.get_all_repositories(limit=900)

    unownedRepos = []
    reposWithMultipleOwners = []
    hmppsRepos = []
    laaRepos = []
    opgRepos = []
    cicaRepos = []
    centralDigitalRepos = []
    platformsAndArchitectureRepos = []
    techServicesRepos = []

    for repository in repositories:
        ownersFound = 0
        if (
            # HMPPS Digital
            "HMPPS Developers" in repository["github_teams_with_any_access"]
            or "HMPPS Developers" in repository["github_teams_with_any_access_parents"]
            # Fuzzy Matches 👇
            or repository["name"].startswith("hmpps-")
        ):
            hmppsRepos.append(repository)
            ownersFound += 1

        if (
            # LAA Digital
            "LAA Technical Architects" in repository["github_teams_with_any_access"]
            or "LAA Technical Architects" in repository["github_teams_with_any_access_parents"]
            or "LAA Developers" in repository["github_teams_with_any_access"]
            or "LAA Developers" in repository["github_teams_with_any_access_parents"]
            or "LAA Crime Apps team" in repository["github_teams_with_any_access"]
            or "LAA Crime Apps team" in repository["github_teams_with_any_access_parents"]
            or "LAA Crime Apply" in repository["github_teams_with_any_access"]
            or "LAA Crime Apply" in repository["github_teams_with_any_access_parents"]
            or "laa-eligibility-platform" in repository["github_teams_with_any_access"]
            or "laa-eligibility-platform" in repository["github_teams_with_any_access_parents"]
            or "LAA Get Access" in repository["github_teams_with_any_access"]
            or "LAA Get Access" in repository["github_teams_with_any_access_parents"]
            or "LAA Payments and Billing" in repository["github_teams_with_any_access"]
            or "LAA Payments and Billing" in repository["github_teams_with_any_access_parents"]
            # Fuzzy Matches 👇
            or repository["name"].startswith("laa-")
        ):
            laaRepos.append(repository)
            ownersFound += 1

        if (
            # OPG Digital
            "OPG" in repository["github_teams_with_any_access"]
            or "OPG" in repository["github_teams_with_any_access_parents"]
            # Fuzzy Matches 👇
            or repository["name"].startswith("opg-")
        ):
            opgRepos.append(repository)
            ownersFound += 1

        if (
            # CICA Digital
            "CICA" in repository["github_teams_with_any_access"]
            or "CICA" in repository["github_teams_with_any_access_parents"]
            # Fuzzy Matches 👇
            or repository["name"].startswith("cica-")
        ):
            cicaRepos.append(repository)
            ownersFound += 1

        if (
            # Central Digital
            "Central Digital Product Team" in repository["github_teams_with_any_access"]
            or "Central Digital Product Team" in repository["github_teams_with_any_access_parents"]
            or "tactical-products" in repository["github_teams_with_any_access"]
            or "tactical-products" in repository["github_teams_with_any_access_parents"]
        ):
            centralDigitalRepos.append(repository)
            ownersFound += 1

        if (
            # Platforms and Architecture https://peoplefinder.service.gov.uk/teams/platforms
            ## Platforms
            contains_one_or_more(
                [
                    ### Hosting Platforms
                    "modernisation-platform",
                    "operations-engineering",
                    "aws-root-account-admin-team",
                    "WebOps",  # Cloud Platform
                    "Studio Webops",  # Digital Studio Operations (DSO)
                    ### Data Platforms
                    "analytical-platform",
                    "data-engineering",
                    "analytics-hq",
                    "data-catalogue",
                    "data-platform",
                    "data-and-analytics-engineering",
                    "observability-platform",
                    ### Publishing Platforms
                    "Form Builder",
                    "Hale platform",
                    "JOTW Content Devs",
                ],
                repository["github_teams_with_any_access"],
            )
            ## Criminal Justice Services
            # Fuzzy Matches 👇
            or repository["name"].startswith("bichard7")
        ):
            platformsAndArchitectureRepos.append(repository)
            ownersFound += 1

        if (
            # Tech Services
            "nvvs-devops-admins" in repository["github_teams_with_any_access"]
            or "nvvs-devops-admins" in repository["github_teams_with_any_access_parents"]
            or "moj-official-techops" in repository["github_teams_with_any_access"]
            or "moj-official-techops" in repository["github_teams_with_any_access_parents"]
        ):
            techServicesRepos.append(repository)
            ownersFound += 1

        if ownersFound == 0:
            unownedRepoCount = unownedRepos.append(repository)

        if ownersFound > 1:
            reposWithMultipleOwners.append(repository)

    unownedRepoCount = len(unownedRepos)
    hmppsRepoCount = len(hmppsRepos)
    laaRepoCount = len(laaRepos)
    opgRepoCount = len(opgRepos)
    cicaRepoCount = len(cicaRepos)
    centralDigitalRepoCount = len(centralDigitalRepos)
    platformsAndArchitectureRepoCount = len(platformsAndArchitectureRepos)
    techServicesRepoCount = len(techServicesRepos)
    reposWithMultipleOwnersCount = len(reposWithMultipleOwners)
    totalRepositories = len(repositories)
    totalFound = totalRepositories - unownedRepoCount

    # Using print here instead of logging so I can pipe the output straight into jq
    print(
        json.dumps(
            {
                "totals": {
                    "totalRepoCount": totalRepositories,
                    "hmppsRepoCount": hmppsRepoCount,
                    "laaRepoCount": laaRepoCount,
                    "opgRepoCount": opgRepoCount,
                    "cicaRepoCount": cicaRepoCount,
                    "centralDigitalRepoCount": centralDigitalRepoCount,
                    "platformsAndArchitectureRepoCount": platformsAndArchitectureRepoCount,
                    "unownedRepoCount": unownedRepoCount,
                    "totalReposWithFoundOwners": totalFound,
                    "reposWithMultipleOwnersCount": reposWithMultipleOwnersCount,
                },
                "percentages": {
                    "hmppsRepoCount": convert_to_percentage(hmppsRepoCount, totalRepositories),
                    "laaRepoCount": convert_to_percentage(laaRepoCount, totalRepositories),
                    "opgRepoCount": convert_to_percentage(opgRepoCount, totalRepositories),
                    "cicaRepoCount": convert_to_percentage(cicaRepoCount, totalRepositories),
                    "centralDigitalRepoCount": convert_to_percentage(centralDigitalRepoCount, totalRepositories),
                    "platformsAndArchitectureRepoCount": convert_to_percentage(platformsAndArchitectureRepoCount, totalRepositories),
                    "techServicesRepoCount": convert_to_percentage(techServicesRepoCount, totalRepositories),
                    "unownedRepoCount": convert_to_percentage(unownedRepoCount, totalRepositories),
                    "totalReposWithFoundOwners": convert_to_percentage(totalFound, totalRepositories),
                    "reposWithMultipleOwnersCount": convert_to_percentage(reposWithMultipleOwnersCount, totalRepositories),
                },
                "repositories": {
                    "hmpps": hmppsRepos,
                    "laa": laaRepos,
                    "opg": opgRepos,
                    "cica": cicaRepos,
                    "centralDigital": centralDigitalRepos,
                    "platformsAndArchitecture": platformsAndArchitectureRepos,
                    "techServices": techServicesRepos,
                    "all": repositories,
                    "unownedRepos": unownedRepos,
                    "reposWithMultipleOwners": reposWithMultipleOwners,
                },
            }
        )
    )


if __name__ == "__main__":
    main()
