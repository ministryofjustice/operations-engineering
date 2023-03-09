import unittest


class TestAssignSupportTicket(unittest.TestCase):
    @patch("sys.argv", ["", "test"])
    def test_main_smoke_test(self, mock1, mock2, mock3):
        add_users_all_org_members_github_team.main()


if __name__ == '__main__':
    unittest.main()
