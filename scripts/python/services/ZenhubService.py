import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class ZenhubService:
    """
    A service to interact with the Zenhub API.
    """

    def __init__(self, api_token: str, repo_id: str) -> None:
        self.zenhub_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.zenhub.com/public/graphql",
            headers={"Authorization": f"Bearer {api_token}"},
        ), execute_timeout=60)
        # set workspace id from GitHub repo id
        self.workspace_id: str = self.get_workspace_id(repo_id)

    def move_issue_to_pipeline(self, issue_to_move, pipeline_id: str):
        print(f"Moving issue {issue_to_move} to pipeline {pipeline_id}")
        move_issue_input = {
            "issueId": issue_to_move,
            "pipelineId": pipeline_id,
        }

        data = self.zenhub_client_gql_api.execute(gql("""
           mutation moveIssue($moveIssueInput: MoveIssueInput!, $workspaceId: ID!) {
              moveIssue(input: $moveIssueInput) {
                issue {
                  id
                  pipelineIssue(workspaceId: $workspaceId) {
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
        """), variable_values={"workspaceId": self.workspace_id, "moveIssueInput": move_issue_input})

        if data["moveIssue"]["issue"]["pipelineIssue"]["pipeline"]["id"] != pipeline_id:
            return TypeError(f"Could not move issue {issue_to_move} to pipeline {pipeline_id}")

    def get_pipeline_id(self, pipeline_name: str) -> str | TypeError:
        data = self.zenhub_client_gql_api.execute(gql("""
            query getPipelinesForWorkspace($workspace_id: ID!) {
              workspace(id: $workspace_id) {
                id
                pipelinesConnection(first: 50) {
                  nodes {
                    id
                    name
                  }
                }
              }
            }
        """), variable_values={"workspace_id": self.workspace_id})

        logging.info(f"Searching for pipeline with name {pipeline_name}")
        if data["workspace"]["pipelinesConnection"]["nodes"] is not None:
            # Return a string of the ID of the pipeline
            for node in data["workspace"]["pipelinesConnection"]["nodes"]:
                if node["name"] == pipeline_name:
                    return node["id"]

        return TypeError(f'Could not find pipeline with name {pipeline_name}')

    def get_workspace_id(self, repository_id: int):
        data = self.zenhub_client_gql_api.execute(gql("""
        query getWorkspacesByRepo($repositoryGhId: [Int!]!) {
          repositoriesByGhId(ghIds: $repositoryGhId) {
            workspacesConnection(first: 50) {
              nodes {
                id
                name
              }
            }
          }
        }
        """), variable_values={"repositoryGhId": [repository_id]})

        if data["repositoriesByGhId"][0]["workspacesConnection"]["nodes"] is not None:
            workspace_id = data["repositoriesByGhId"][0]["workspacesConnection"]["nodes"][0]["id"]
            return workspace_id

    def search_issues_by_label(self, pipeline_id: str, label: str):
        """
        Search for issues in a pipeline (a column in Zenhub) with a specific label
        Args:
            pipeline_id: The ID of the pipeline to search in (you can get this from the Zenhub API).
            label: The label attached to the GitHub issue.

        Returns:

        """
        data = self.zenhub_client_gql_api.execute(gql("""
        query($pipelineId: ID!, $label: String!){
            searchIssuesByPipeline(
                pipelineId: $pipelineId,
                filters: {
                    labels: { in: [$label]}
                }
            ) {
              nodes {
                  id
                  number
                  title
              }
            }
            }
        """), variable_values={"pipelineId": pipeline_id, "label": label})

        return data["searchIssuesByPipeline"]["nodes"]
