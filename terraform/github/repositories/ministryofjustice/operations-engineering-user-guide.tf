# module "operations-engineering-user-guide" {
#   source  = "ministryofjustice/repository/github"
#   version = "1.2.1"

#   poc = false

#   name         = "operations-engineering-user-guide"
#   description  = "User documentation for Operations Engineering"
#   homepage_url = "https://user-guide.operations-engineering.service.justice.gov.uk/"
#   topics       = ["operations-engineering", "documentation", "user-guides"]

#   team_access = {
#     admin = [var.operations_engineering_team_id]
#   }
# }
