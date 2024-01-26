module "operations-engineering-reports" {
  source = "github.com/ministryofjustice/operations-engineering-terraform-github-repository?ref=0.0.2"

  name             = "operations-engineering-reports"
  application_name = "operations-engineering-reports"
  description      = "Web application to receive JSON data and display data in reports using HTML."
  homepage_url     = "https://operations-engineering-reports.cloud-platform.service.justice.gov.uk/"
  topics           = ["flask", "reporting"]
  tags = {
    Team  = "operations-engineering"
    Phase = "production"
  }
}