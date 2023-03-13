from github import Github
import requests
import os

# GitHub Config
organization = "ministryofjustice"
team_slug = "operations-engineering"
dependabot_labels = ["dependencies"]

# ZenHub Config
graphql_url = "https://api.zenhub.com/public/graphql"
workspace_id = "614da9b850253700151e7252"

# Auth
# This is used by GitHub Actions for final version
# git = Github(os.getenv("ADMIN_GITHUB_TOKEN"))
#zh_token = os.getenv("ZENHUB_ADMIN_TOKEN")
zh_token = "ZENHUB TOKEN GOES HERE FOR LOCAL"
git = Github("GITHUB TOKEN GOES HERE FOR LOCAL")

# Get all open Dependabot issues for all the teams repos for that particular org
# This returns a list of PRs for all our repos in GitHub
# The reason I did this instead of just detect them in ZenHub is incase we ever move to ZenHub
# issues = [issue for repo in [repo.get_issues(state="open", labels=dependabot_labels)
#                              for repo in git.get_organization(organization).get_team_by_slug(team_slug).get_repos()] for issue in repo]


# Try and get ZenHub API to move the ticket (this isn't working right now)
def move_ticket(issue_id, pipeline_id, position=3, workspace_id=workspace_id):
    
    headers = {"Authorization": f"Bearer {zh_token}"}
    
    moveIssueInput = {
        "moveIssueInput": {
            "pipelineId": "{pipeline_id}",
            "issueId": "{issue_id}",
            "position": position
        }
    }
    
    graphql = """
    mutation moveIssue($MoveIssueInput: MoveIssueInput! = {moveIssueInput}, $WorkspaceId: ID! = {workspace_id}) {
      moveIssue(input: $MoveIssueInput) {
        issue {
          id
          pipelineIssue(workspaceId: $WorkspaceId) {
            priority {
              id
              name
              color
            }
            pipeline {
              id
            }
          }
        }
      }
    }
    """
    
    print(requests.post(graphql_url, data=graphql, headers=headers).json())



# Trying to get ^ method to work - this will need to take the ID from the line 24 for each PR as issue_id for final version.
move_ticket(issue_id=388, pipeline_id="Refined and Ready")
