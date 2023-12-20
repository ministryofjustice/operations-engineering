import os
import pickle
import pandas as pd
import numpy as np
from collections import Counter
import shutil

from services.github_service import GithubService


def get_environment_variables() -> tuple:
    github_token = os.getenv("ADMIN_GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "The env variable ADMIN_GITHUB_TOKEN is empty or missing")

    return github_token

def main():

    github_token = get_environment_variables()
    org = "ministryofjustice"
    github_service = GithubService(github_token, org)

    path = "temp-data"
    if not os.path.exists(path):
        os.makedirs("temp-data")

    # Get topics per repo
    n_topics = 12
    github_repos_and_topics = github_service.get_org_repo_name_and_first_n_topics(n_topics=n_topics)
    # Save
    with open(f"temp-data/github-repos-and-{n_topics}-topics", "wb") as fp:
        pickle.dump(github_repos_and_topics, fp)

    # Create df of repos and lists of topics
    repo_names = [r[0] for r in github_repos_and_topics]
    topic_list = [r[1] for r in github_repos_and_topics]
    d = {"repository_name": repo_names, "topic_list": topic_list}
    df = pd.DataFrame(d)
    df = df.sort_values(by="repository_name")
    df["n_topics"] = df["topic_list"].apply(lambda x: len(x))
    df.to_csv("temp-data/repo_names_and_topics.csv", index=False)

    # Print out all repos with operations-engineering topic or prefix
    opseng_prefixed_repos = df[df.repository_name.str.contains(r"^operations-engineering*")]["repository_name"].to_list()

    df = df.explode("topic_list").reset_index(drop=True).dropna()
    opseng_topic_repos = df[df.topic_list.str.contains(r"^operations-engineering*")]["repository_name"].to_list()

    opseng_related_repos = sorted(list(set(opseng_prefixed_repos).union(set(opseng_topic_repos))))
    print(opseng_related_repos)

    # Remove temp folder
    shutil.rmtree("temp-data")


if __name__ == "__main__":
    main()