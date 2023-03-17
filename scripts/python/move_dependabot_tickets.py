import argparse
import logging

from services.ZenhubService import ZenhubService


def get_issues(zenhub: ZenhubService, label, from_pipeline: str) -> list | Exception:
    from_pipeline_id = zenhub.get_pipeline_id(from_pipeline)
    if from_pipeline_id is None:
        logging.error(
            f"Failed to get pipeline ID for pipeline {from_pipeline}")
        raise ValueError

    return zenhub.search_issues_by_label(from_pipeline_id, label)


def move_issues(zenhub: ZenhubService, issues_to_move, to_pipeline) -> Exception:
    to_pipeline_id = zenhub.get_pipeline_id(to_pipeline)
    if to_pipeline_id is None:
        logging.error(f"Failed to get pipeline ID for pipeline {to_pipeline}")
        raise ValueError

    for issue in issues_to_move:
        logging.info(f"Moving issue {issue['id']} to pipeline {to_pipeline}")
        success = zenhub.move_issue_to_pipeline(issue['id'], to_pipeline_id)
        if not success:
            logging.error(
                f"Failed to move issue {issue['id']} to pipeline {to_pipeline}")
            return Exception

    return None


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
        "--label",
        type=str,
        default="dependencies",
        help="The label attached to the GitHub issue.",
    )

    parser.add_argument(
        "--from_pipeline",
        type=str,
        default="New Issues",
        help="The name of the pipeline to move the issue from.",
    )

    parser.add_argument(
        "--to_pipeline",
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

    zenhub = ZenhubService(args.api_token)
    zenhub.workspace_id = zenhub.get_workspace_id_from_repo(args.repo_id)

    try:
        issues = get_issues(zenhub, args.label, args.from_pipeline)
    except Exception as e:
        return e

    logging.warn(issues)

    if len(issues) == 0:
        logging.info("Nothing to move, closing")
        return

    try:
        move_issues(zenhub, issues, args.to_pipeline)
    except Exception as e:
        return e


if __name__ == "__main__":
    main()
