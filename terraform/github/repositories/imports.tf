# Imports to ministryofjustice-test org team_id 9472191
import {
  to = module.test_tamf_repo_test_org.github_team_repository.push["9472191"]
  id = "9472191:test-tamf-repo-test-org"
}

# Imports to ministryofjustice operations-engineering team_id 4192115 with admin access
# import {
#   to = module.acronyms.github_team_repository.admin["4192115"]
#   id = "4192115:acronyms"
# }

# import {
#   to = module.cloud-platform-maintenance-pages.github_team_repository.admin["4192115"]
#   id = "4192115:cloud-platform-maintenance-pages"
# }

locals {
  repositories = {
    "acronyms"                         = "admin"
    "cloud-platform-maintenance-pages" = "admin"
  }
}

import {
  for_each = local.repositories
  to       = module.each.key.github_team_repository.each.value["4192115"]
  id       = "4192115:${each.key}"
}