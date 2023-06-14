import unittest
import tempfile
import os
from datetime import datetime

from python.scripts import document_review_checker as check


class TestDocumentReviewChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.file_path = tempfile.mkdtemp()

    def test_documents_due_for_review(self):
        with tempfile.NamedTemporaryFile(
                dir=self.file_path, delete=False, suffix=".md.erb") as file:
            file.write(b"last_reviewed_on: 2020-03-14")
            file.close()

        self.addCleanup(os.remove, file.name)

        documents = check.get_documents_due_for_review(self.file_path)
        self.assertIn(file.name, documents)

    def test_no_documents_to_review(self):
        today = datetime.today()
        with tempfile.NamedTemporaryFile(
                dir=self.file_path, delete=False, suffix=".md.erb") as file:
            file.write(b"last_reviewed_on: %s" %
                       today.strftime("%Y-%m-%d").encode())
            file.close()

        self.addCleanup(os.remove, file.name)

        documents = check.get_documents_due_for_review(self.file_path)
        self.assertNotIn(file.name, documents)


class TestFixingDocumentDates(unittest.TestCase):
    def setUp(self) -> None:
        self.fix = True
        self.file_path = tempfile.mkdtemp()

    def test_with_file_to_fix(self):
        with tempfile.NamedTemporaryFile(
                dir=self.file_path, delete=False, suffix=".md.erb") as file:
            file.write(b"last_reviewed_on: 2020-03-14")
            file.close()

        self.addCleanup(os.remove, file.name)

        documents = check.get_documents_due_for_review(self.file_path)
        self.assertIn(file.name, documents)

        check.fix_date(file.name)

        documents = check.get_documents_due_for_review(self.file_path)
        self.assertNotIn(file.name, documents)


if __name__ == "__main__":
    unittest.main()
