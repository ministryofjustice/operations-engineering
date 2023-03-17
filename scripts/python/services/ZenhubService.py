import logging

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class ZenhubService:
    """
    A class to interact with the Zenhub API using GraphQL queries.

    Args:
        api_token (str): The API token to use for the Zenhub API. You can generate
            one from https://app.zenhub.com/dashboard/tokens.

    Attributes:
        zenhub_client_gql_api (Client): A GraphQL client to interact with the Zenhub API.
        workspace_id (str): The ID of the workspace to use for queries.
    """

    def __init__(self, api_token: str) -> None:
        self._workspace_id = None
        self.zenhub_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.zenhub.com/public/graphql",
            headers={"Authorization": f"Bearer {api_token}"},
        ), execute_timeout=60)

    def move_issue_to_pipeline(self, issue_to_move, to_pipeline: str) -> bool:
        """
        Move a zenhub issue to a pipeline regardless of the current pipeline.

        Args:
            issue_to_move: a string of the issue ID to move
            to_pipeline: a string of the pipeline ID to move the issue to

            both of these values can be obtained from the Zenhub API.

        Returns:
            bool: True if the issue was moved successfully, False otherwise.
        """
        move_issue_input = {
            "issueId": issue_to_move,
            "pipelineId": to_pipeline,
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
        """), variable_values={"workspaceId": self._workspace_id, "moveIssueInput": move_issue_input})

        if data["moveIssue"]["issue"]["pipelineIssue"]["pipeline"]["id"] != to_pipeline:
            return False

        return True

    def get_pipeline_id(self, pipeline_name: str) -> str | None:
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
        """), variable_values={"workspace_id": self._workspace_id})

        logging.info(f"Searching for pipeline with name {pipeline_name}")
        if data["workspace"]["pipelinesConnection"]["nodes"] is not None:
            # Return a string of the ID of the pipeline
            for node in data["workspace"]["pipelinesConnection"]["nodes"]:
                if node["name"] == pipeline_name:
                    return node["id"]

        return None

    @property
    def workspace_id(self) -> int:
        return self._workspace_id

    @workspace_id.setter
    def workspace_id(self, workspace_id: int):
        self._workspace_id = workspace_id

    def get_workspace_id_from_repo(self, repository_id: int):
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

        try:
            if data["repositoriesByGhId"][0]["workspacesConnection"]["nodes"] is not None:
                workspace_id = data["repositoriesByGhId"][0]["workspacesConnection"]["nodes"][0]["id"]
                return workspace_id
            else:
                return Exception(f'Could not find workspace for repository with ID {repository_id}')
        except IndexError:
            return Exception(f'Could not find workspace for repository with ID {repository_id}')

    def search_issues_by_label(self, pipeline_id: str, label: str):
        """
        Search for issues in a pipeline (a column in Zenhub) with a specific label
        Args:
            pipeline_id: The ID of the pipeline to search in (you can get this from the Zenhub API).
            label: The label attached to the GitHub issue.

        Returns:
            A list of issues with the label in the pipeline.

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
