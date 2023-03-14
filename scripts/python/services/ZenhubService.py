from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class ZenhubService:
    """
    A service to interact with the Zenhub API.
    """
    def __init__(self, api_token: str, organisation_name: str) -> None:
        self.zenhub_client_gql_api: Client = Client(transport=AIOHTTPTransport(
            url="https://api.zenhub.com/public/graphql",
            headers={"Authorization": f"Bearer {api_token}"},
        ), execute_timeout=60)
        self.organisation_name: str = organisation_name

    def get_pipeline_id(self, workspace_id: str, pipeline_name: str) -> str | TypeError:
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
        """), variable_values={"workspace_id": workspace_id})

        if data["workspace"]["pipelineConnection"]["nodes"] is not None:
            for pipeline in data["workspace"]["pipelineConnection"]["nodes"]:
                if pipeline.name == pipeline_name:
                    return pipeline.id

        return TypeError(f"Could not find pipeline with name {pipeline_name}")

    def get_workspace_id(self, repository_id: str) -> str | TypeError:
        data = self.zenhub_client_gql_api.execute(gql("""
        query getWorkspacesByRepo($repositoryGhId: [Int!]!) {
          repositoriesByGhId(ghIds: $repositoryGhId) {
            id
            workspacesConnection(first: 50) {
              nodes {
                id
                name
                description
                repositoriesConnection(first: 50) {
                  nodes {
                    id
                    ghId
                    name
                  }
                }
              }
            }
          }
        }
        """), variable_values={"repository_id": repository_id})

        if data["repositoriesByGhId"]["workspacesConnection"]["nodes"] is not None:
            return data["repositoriesByGhId"]["workspacesConnection"]["nodes"][0]["id"]

        return TypeError(f"Could not find workspace for repository with ID {repository_id}")

    def search_issue_by_label(self, pipeline_id: str, label: str):
        """
        Search for issues in a pipeline (a column in Zenhub) with a specific label
        Args:
            pipeline_id: The ID of the pipeline to search in (you can get this from the Zenhub API).
            label: The label attached to the GitHub issue.

        Returns:

        """
        data = self.zenhub_client_gql_api.execute(gql("""
            query {
                searchIssuesByPipeline(
                    pipelineId: $pipline_id,
                    filters: {
                        labels: { in: [$label] }
                    }
                ) {
                  nodes {
                      id
                      number
                      title
                  }
            }
            }
        """), variable_values={"pipeline_id": pipeline_id, "label": label})

        return data["searchIssuesByPipeline"]["nodes"]

