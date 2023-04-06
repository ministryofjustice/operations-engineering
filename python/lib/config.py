import os
from pyaml_env import parse_config


class Config:
    """This class wraps the config file values"""

    def __init__(self):
        config_file = os.getenv("CONFIG_FILE")
        if config_file == "" or config_file is None:
            raise ValueError(
                "The env variable CONFIG_FILE is empty or missing")

        self.configs = parse_config(
            f"{os.path.dirname(os.path.realpath(__file__))}/../config/{config_file}")

        self.badly_named_repositories = []
        if self.configs["badly_named_repositories"] is not None:
            self.badly_named_repositories = [
                repo_name.lower() for repo_name in self.configs["badly_named_repositories"]]

        self.ignore_teams = []
        if self.configs["ignore_teams"] is not None:
            self.ignore_teams = [team_name.lower()
                                 for team_name in self.configs["ignore_teams"]]
