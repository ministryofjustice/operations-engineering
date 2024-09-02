import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from services.github_service import GithubService

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
    "jwt-laminas-auth",
    "laa-eric-emi",
    "hmpps-alfresco",
    "yjaf-mule-mis-processor",
    "satis-s3",
    "wasm",
    "wp-rewrite-media-to-s3",
    "oracle-policy-automation-docker",
    "Transport",  # keep repo in list until collaborator Arcturus-Tom is removed
    "HMLandsRegistry",  # keep repo in list until collaborator Arcturus-Tom is removed
    "LandsChamberTribunal",  # keep repo in list until collaborator Arcturus-Tom is removed
    # keep repo in list until collaborator Arcturus-Tom is removed
    "FinanceAndTaxTribunalDecision",
    "InformationTribunal",  # keep repo in list until collaborator Arcturus-Tom is removed
    "HMEat",  # keep repo in list until collaborator Arcturus-Tom is removed
    "Cicap",  # keep repo in list until collaborator Arcturus-Tom is removed
    "CareStandards",  # keep repo in list until collaborator Arcturus-Tom is removed
    "AdministrativeAppeals",  # keep repo in list until collaborator Arcturus-Tom is removed
    "laa-ccms-opa-interview-initialiser",
    "yjaf-gateway-proxy",  # keep repo in list until collaborator is removed
    "safety-diagnostic-tool",
    "staff-infrastructure-print-xwc",
    "laa-ccms-service-adapter",
]

MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME = "moj-analytical-services"
MOJ_ANALYTICAL_SERVICES_REPOS_ALLOW_LIST = [
    "timeliness_ctx",
    "GPC-anomalies",
    "pq-tool",
    "opg-data-processing",
    "df_criminal_court_research",
    "criminal-forecasting-rap",
    "airflow-matrix-scraper",
    "airflow-shs-qual",
    "airflow-assaults-reasons-locations",
    "airflow-spells-correction",
    "airflow-viper",
    "airflow-viper-test",
    "airflow-sh-location",
    "airflow-sdt-extras",
    "airflow-sdt",
    "airflow-viper-to-external-ds",
    "shinyGovstyle",
    "segmentation-data-creation",
]


def get_environment_variables() -> tuple[str, str]:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError("The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    github_organization_name = os.getenv("GITHUB_ORGANIZATION_NAME")
    if not github_organization_name:
        raise ValueError("The env variable GITHUB_ORGANIZATION is empty or missing")

    return github_token, github_organization_name


def get_config_for_organization(
    github_organization_name: str,
) -> tuple[datetime, str, list[str]] | ValueError:
    last_active_cutoff_date = datetime.now() - relativedelta(days=0, months=6, years=1)

    if github_organization_name == MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME:
        return (
            last_active_cutoff_date,
            MINISTRYOFJUSTICE_GITHUB_ORGANIZATION_NAME,
            MINISTRYOFJUSTICE_REPOS_ALLOW_LIST,
        )

    if github_organization_name == MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME:
        return (
            last_active_cutoff_date,
            MOJ_ANALYTICAL_SERVICES_GITHUB_ORGANIZATION_NAME,
            MOJ_ANALYTICAL_SERVICES_REPOS_ALLOW_LIST,
        )

    raise ValueError(
        f"Unsupported Github Organization Name [{github_organization_name}]"
    )


def main():
    github_token, github_organization_name = get_environment_variables()
    last_active_cutoff_date, organization_name, allow_list = (
        get_config_for_organization(github_organization_name)
    )
    GithubService(github_token, organization_name).archive_all_inactive_repositories(
        last_active_cutoff_date, allow_list
    )


if __name__ == "__main__":
    main()
