resource "github_team" "ops_eng_support" {
  name        = "operations-engineering-support"
  description = "Team for support engineers"
  privacy     = "closed"
}

resource "github_team_membership" "ops_eng_support_memberships" {
  for_each = toset(var.ops_eng_support_members)
  team_id  = github_team.ops_eng_support.id
  username = each.value
  role     = "member"
}
