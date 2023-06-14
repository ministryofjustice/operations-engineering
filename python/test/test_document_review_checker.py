import unittest
import tempfile

import python.scripts.document_review_checker as document_review_checker

class TestDocumentReviewChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.fix = True
        self.file_path = "."


    def test_get_documents_due_for_review(self):
        # create a test file in the current directory
        # call the function
        # assert that the file is in the list
        # TODO: Make sure you defer the file deletion until after the test
        file = tempfile.NamedTemporaryFile(dir=self.file_path, delete=False)
        file.write(b"last_reviewed_on: 2022-03-14")
        file.close()

        documents = document_review_checker.get_documents_due_for_review()
        print(documents)
        self.assertIn(file.name, documents)


if __name__ == "__main__":
    unittest.main()
