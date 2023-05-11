from github import Github
import logging

# This class is an interface for interacting with a GitHub org and its repos at an admin level, it can be pointed at any org
# But please be aware it has been written with the moj-analytical-services org in mind


class MojGithub:

    # Logging Config
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def __init__(self, org: str, org_token: str) -> None:
        self.git = Github(org_token)
        self.org = self.git.get_organization(org)
        self.__repos = None
        self.__public_repos = None
        self.__private_repos = None

    @property
    def repos(self) -> list:
        """Returns all repos for given organization.\n
        This does include archived repos.\n
        This does not include forks repos.\n
        Please see the function get_unarchived_repos to ommit archived repos
        """
        if self.__repos is None:
            self.__repos = self._get_repo_type(repo_type="all")
        return self.__repos

    @property
    def public_repos(self) -> list:
        """Returns all public repos for given organization\n
        This does include archived repos.\n
        This does not include forks repos.\n
        Please see the function get_unarchived_repos to ommit archived repos
        """
        if self.__public_repos is None:
            self.__public_repos = self._get_repo_type(repo_type="public")
        return self.__public_repos

    @property
    def private_repos(self) -> list:
        """Returns all private repos for given organization.\n
        This does include archived repos.\n
        This does not include forks repos.\n
        Please see the function get_unarchived_repos to ommit archived repos
        """
        if self.__private_repos is None:
            self.__private_repos = self._get_repo_type(repo_type="private")
        return self.__private_repos

    def get_unarchived_repos(self, repo_type: str) -> list:
        """Returns all repos of a specific repo type omitting the archived ones.\n
        repo_type:
        * all
        * public
        * private
        """
        match repo_type:
            case "all":
                return self._exclude_archived_repos(self.repos)
            case "public":
                return self._exclude_archived_repos(self.public_repos)
            case "private":
                return self._exclude_archived_repos(self.private_repos)
            case "_":
                logging.error(
                    f"MojGithub.get_unarchived_repos called with incorrect parameter: {type}"
                )

    def _exclude_archived_repos(self, repos: list) -> list:
        """NOTE: Internal function used by libary, please use with care\n
        Filters out archived repos from a list of repos
        """
        return list(filter(lambda x: x.archived is False, repos))

    def _exclude_fork_repos(self, repos: list) -> list:
        """NOTE: Internal function used by libary, please use with care\n
        Filters out forked repos from a list of repos
        """
        return list(filter(lambda x: x.fork is False, repos))

    def _get_repo_type(self, repo_type: str) -> list:
        """NOTE: Internal function used by libary, please use with care\n
        Returns all orgs for a given repository type\n
        This function does not return fork repos\n
        Please refer to following properties for proper usage:
        * repos
        * public_repos
        * private_repos

        repo_type:
        * all
        * public
        * private
        """
        return self._exclude_fork_repos(list(self.org.get_repos(type=repo_type)))
