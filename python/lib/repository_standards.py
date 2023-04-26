class RepositoryStandards:
    class Report:
        """
        Class to hold the report standards
        """

        def __init__(self, repo_data):
            """
            Single repository data as Hash/JSON
            """
            self.repo_data = repo_data

        def structure(self):
            """
            The structure of the report to write to file as a Hash data type

            :return: Hash
            """
            return {
                "name": repo_name(),
                "default_branch": default_branch(),
                "url": repo_url(),
                "last_push": last_push(),
                "report": all_checks_result(),
                "is_private": is_private(),
            }

        def repo_name(self):
            """
            Repository name

            :return: String
            """
            return self.repo_data.dig["name"]
