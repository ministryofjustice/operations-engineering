import argparse
import logging

from services.ZenhubService import ZenhubService


def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_token",
        type=str,
        required=True,
        help="The zenhub api token to use.",
    )

    parser.add_argument(
        "--repo_id",
        type=str,
        default="223385041",  # This is the ID of the "operations-engineering" repo
        help="The ID of the GitHub Repository to search for the zenhub workspace",
    )

    return parser.parse_args()


def main():
    args = add_arguments()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("Starting script")
    zenhub = ZenhubService(args.api_token)

    # Get the ID of the workspace to search in
    try:
        workspace_id = zenhub.get_workspace_id(args.repo_id)
    except Exception as e:
        logging.error("Failed to get workspace ID")
        logging.error(e)
        return

    # Get the ID of the pipeline to search in
    try:
        pipeline_id = zenhub.get_pipeline_id(workspace_id, "Support")
    except Exception as e:
        logging.error("Failed to get pipeline ID")
        logging.error(e)
        return

    # Get the issues in the pipeline
    try:
        issues = zenhub.get_issues_in_pipeline(pipeline_id)
    except Exception as e:
        logging.error("Failed to get issues in pipeline")
        logging.error(e)
        return

    # Print the issues
    for issue in issues:
        logging.info(issue)

    logging.info("Finished script")
