import os
from pyaml_env import parse_config


class Config:
    """This class wraps the config file values"""

    def __init__(self):
        config_file = os.getenv("CONFIG_FILE")
        if config_file == "" or config_file is None:
            raise ValueError(
                "The env variable CONFIG_FILE is empty or missing")

        self.config = parse_config(
            f"{os.path.dirname(os.path.realpath(__file__))}/../config/{config_file}")

    def get_badly_named_repositories(self):
        badly_named_repositories = []
        if self.config["badly_named_repositories"] is not None:
            badly_named_repositories = self.config["badly_named_repositories"]
        return badly_named_repositories

    def get_ignore_teams(self):
        ignore_teams = []
        if self.config["ignore_teams"] is not None:
            ignore_teams = self.config["ignore_teams"]
        return ignore_teams
