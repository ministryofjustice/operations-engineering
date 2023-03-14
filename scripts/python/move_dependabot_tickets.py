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
        type=int,
        default=223385041,  # This is the ID of the "operations-engineering" repo
        help="The ID of a GitHub repository that exists in your Zenhub workspace.",
    )

    parser.add_argument(
        "--label_to_move",
        type=str,
        default="dependencies",
        help="The label attached to the GitHub issue.",
    )

    parser.add_argument(
        "--pipeline_to_move_from",
        type=str,
        default="New Issues",
        help="The name of the pipeline to move the issue from.",
    )

    parser.add_argument(
        "--pipeline_to_move_to",
        type=str,
        default="Refined and Ready",
        help="The name of the pipeline to move the issue to.",
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
        pipeline_id = zenhub.get_pipeline_id(workspace_id, args.pipeline_to_move_from)
    except Exception as e:
        logging.error("Failed to get pipeline ID")
        logging.error(e)
        return

    # Get the issues in the pipeline
    try:
        issues = zenhub.search_issue_by_label(pipeline_id, args.label_to_move)
    except Exception as e:
        logging.error("Failed to get issues in pipeline")
        logging.error(e, exc_info=True)
        return

    # Print the issues
    for issue in issues:
        logging.info(issue)

    logging.info("Finished script")


if __name__ == "__main__":
    main()
