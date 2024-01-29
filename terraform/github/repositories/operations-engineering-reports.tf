module "operations-engineering-reports" {
  source  = "ministryofjustice/repository/github"
  version = "0.0.3"

  name             = "operations-engineering-reports"
  application_name = "operations-engineering-reports"
  description      = "Web application to receive JSON data and display data in reports using HTML."
  homepage_url     = "https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/"
  topics           = ["flask", "reporting"]
}