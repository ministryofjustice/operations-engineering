import unittest
import tempfile
import os

from python.scripts import document_review_checker as check

class TestDocumentReviewChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.fix = True
        self.file_path = tempfile.mkdtemp()


    def test_get_documents_due_for_review(self):
        with tempfile.NamedTemporaryFile(
            dir=self.file_path, delete=False, suffix=".md.erb") as file:
            file.write(b"last_reviewed_on: 2020-03-14")
            file.close()

        self.addCleanup(os.remove, file.name)

        documents = check.get_documents_due_for_review(self.file_path)
        self.assertIn(file.name, documents)


if __name__ == "__main__":
    unittest.main()
