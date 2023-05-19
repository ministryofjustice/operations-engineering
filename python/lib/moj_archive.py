import logging

from github import Repository


# This class handles the archiving of one GitHub repository


class MojArchive:
    # Logging Config
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def __init__(self, repo: Repository.Repository, allow_list: list[str]) -> None:
        self.__repo = repo
        # Not currently used for functionality, included incase we want to perform actions like posting issues to the repo in which we need this to track
        self.__complete = False
        self.__allow_list = allow_list

    @property
    def archived(self) -> bool:
        """Property for returning the underlying PyGithub Repository objects archive value"""
        return self.repo.archived

    @property
    def repo(self) -> Repository.Repository:
        """Property for returning the underlying PyGithub Repository object."""
        return self.__repo

    @property
    def complete(self) -> bool:
        """Property for if the target repository has been archived."""
        return self.__complete

    @complete.setter
    def complete(self, value: bool) -> None:
        """Property for if the target repository has been archived
        value: bool
        """
        self.__complete = value

    @property
    def is_on_allow_list(self) -> bool:
        """Returns if the target repository is on the allow list or not"""
        return True if self.repo.name in self.__allow_list else False

    def archive(self) -> bool:
        """Archives the target repository.\n
        Returns True if successful or on allow list, False otherwise.
        """
        if self.is_on_allow_list:
            logging.info(
                f"Skipping repository:  {self.repo.name}, Reason: Present in allow list "
            )
            return True

        # Archive the repository
        self.repo.edit(archived=True)

        # Check it has been archived, report status and set complete flag
        if self.archived:
            self.complete = True
            logging.info(
                f"Archiving repository: {self.repo.name}, Status: Successful")
            return True
        else:
            logging.error(
                f"Archiving repository: {self.repo.name}, Status: Failure")
            return False
