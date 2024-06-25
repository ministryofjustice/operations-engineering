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


def main():
    github_token, repository_limit = get_environment_variables()
    github_service = GithubService(github_token, "ministryofjustice")
    repositories = github_service.get_all_repositories(limit=repository_limit)

    unownedRepos = []
    reposWithMultipleOwners = []
    hmppsRepos = []
    laaRepos = []
    opgRepos = []
    centralDigitalRepos = []
    platformsAndArchitectureRepos = []

    for repository in repositories:
        ownersFound = 0
        if (
            repository["name"].startswith("hmpps-")
            or "HMPPS Developers" in repository["github_teams_with_any_access"]
            or "HMPPS Developers" in repository["github_teams_with_any_access_parents"]
            or "Digital Studio Sheffield" in repository["github_teams_with_any_access"]
            or "Digital Studio Sheffield" in repository["github_teams_with_any_access_parents"]
        ):
            hmppsRepos.append(repository)
            ownersFound += 1

        if (
            repository["name"].startswith("laa-")
            or "LAA Technical Architects" in repository["github_teams_with_any_access"]
            or "LAA Technical Architects" in repository["github_teams_with_any_access_parents"]
            or "LAA Developers" in repository["github_teams_with_any_access"]
            or "LAA Developers" in repository["github_teams_with_any_access_parents"]
        ):
            laaRepos.append(repository)
            ownersFound += 1

        if (
            repository["name"].startswith("opg-")
            or "OPG" in repository["github_teams_with_any_access"]
            or "OPG" in repository["github_teams_with_any_access_parents"]
        ):
            opgRepos.append(repository)
            ownersFound += 1

        if (
            "Central Digital Product Team" in repository["github_teams_with_any_access"]
            or "Central Digital Product Team" in repository["github_teams_with_any_access_parents"]
            or "tactical-products" in repository["github_teams_with_any_access"]
            or "tactical-products" in repository["github_teams_with_any_access_parents"]
        ):
            centralDigitalRepos.append(repository)
            ownersFound += 1

        if (
            repository["name"].startswith("modernisation-platform")
            or "modernisation-platform" in repository["github_teams_with_admin_access"]
            or repository["name"].startswith("cloud-platform")
            or repository["name"].startswith("operations-engineering")
            or "operations-engineering" in repository["github_teams_with_admin_access"]
            or repository["name"].startswith("analytics-platform")
            or repository["name"].startswith("analytical-platform")
            or "analytical-platform" in repository["github_teams_with_admin_access"]
            or repository["name"].startswith("data-platform")
            or repository["name"].startswith("observability-platform")
            or "observability-platform" in repository["github_teams_with_admin_access"]
        ):
            platformsAndArchitectureRepos.append(repository)
            ownersFound += 1

        if ownersFound == 0:
            unownedRepoCount = unownedRepos.append(repository)

        if ownersFound > 1:
            reposWithMultipleOwners.append(repository)

    unownedRepoCount = len(unownedRepos)
    hmppsRepoCount = len(hmppsRepos)
    laaRepoCount = len(laaRepos)
    opgRepoCount = len(opgRepos)
    centralDigitalRepoCount = len(centralDigitalRepos)
    platformsAndArchitectureRepoCount = len(platformsAndArchitectureRepos)
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
                    "centralDigitalRepoCount": convert_to_percentage(centralDigitalRepoCount, totalRepositories),
                    "platformsAndArchitectureRepoCount": convert_to_percentage(platformsAndArchitectureRepoCount, totalRepositories),
                    "unownedRepoCount": convert_to_percentage(unownedRepoCount, totalRepositories),
                    "totalReposWithFoundOwners": convert_to_percentage(totalFound, totalRepositories),
                    "reposWithMultipleOwnersCount": convert_to_percentage(reposWithMultipleOwnersCount, totalRepositories),
                },
                "repositories": {
                    "hmpps": hmppsRepos,
                    "laa": laaRepos,
                    "opg": opgRepos,
                    "centralDigital": centralDigitalRepos,
                    "platformsAndArchitecture": platformsAndArchitectureRepos,
                    "all": repositories,
                    "unownedRepos": unownedRepos,
                    "reposWithMultipleOwners": reposWithMultipleOwners,
                },
            }
        )
    )


if __name__ == "__main__":
    main()
