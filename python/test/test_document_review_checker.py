import unittest
import tempfile
import os
from datetime import datetime

from python.scripts import document_review_checker as check


class TestDocumentReviewChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.file_path = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(
            dir=self.file_path, delete=False, suffix=".md.erb") as self.file:
            self.file.write(b"last_reviewed_on: 2020-03-14")
            self.file.close()


    def tearDown(self) -> None:
        self.addCleanup(os.remove, self.file.name)


    def test_documents_due_for_review(self):
        documents = check.get_documents_due_for_review(self.file_path)
        self.assertIn(self.file.name, documents)

    def test_no_documents_to_review(self):
        new_file_path = tempfile.mkdtemp()
        documents = check.get_documents_due_for_review(new_file_path)
        self.assertNotIn(self.file.name, documents)


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
