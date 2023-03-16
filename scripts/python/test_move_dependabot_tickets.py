import unittest
from unittest.mock import patch, MagicMock

import move_dependabot_tickets


class TestMoveDependabotTickets(unittest.TestCase):

    @patch("gql.Client.__new__", new=MagicMock())
    @patch("sys.argv", ["", "--api_token", "test"])
    def test_main(self):
        self.assertRaises(ValueError, move_dependabot_tickets.main)


if __name__ == '__main__':
    unittest.main()
