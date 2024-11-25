module "acronyms" {
  source  = "ministryofjustice/repository/github"
  version = "1.2.1"

  poc = false

  name        = "acronyms"
  description = "List of abbreviations used within the MoJ, and their definitions"
  topics      = ["operations-engineering"]
}
