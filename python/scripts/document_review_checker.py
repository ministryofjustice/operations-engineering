"""The document review checker module allows the caller
to generate a list of documents that are due for review.

As part of the support process in Operations Engineering,
we have a number of documents that need to be reviewed
on a three month cycle.

The caller of this script can generate a list of documents
that are due for review based on the current date, pass them
to their editor of choice, and then update the document the date
as they see fit.

Stript execution:
python python/scripts/document_review_checker.py --help
"""
import argparse
import os
import re
from datetime import datetime

def get_documents_due_for_review(file_path: str) -> list[str]:
    """Return a list of documents that are due for review"""
    list_of_documents = []
    for root, _, files in os.walk(file_path, topdown=True):
        # if the file is a markdown file
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".md.erb") and __needs_review(file_path):
                list_of_documents.append(file_path)

    return list_of_documents


def __needs_review(document: str) -> bool:
    today = datetime.today()
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    print("checking document", document)


    with open(document, 'r') as file:
        content = file.read()
        match = re.search(date_pattern, content)
        if match:
            date_str = match.group()
            date_format = "%Y-%m-%d"

            date_obj = datetime.strptime(date_str, date_format)
            if date_obj < today:
                return True

    return False

def __fix_document(document: str) -> None:
    print(f"Fixing document {document}")
    pass

def main():
    parser = argparse.ArgumentParser(description="Document review checker")
    parser.add_argument("--fix", action="store_true",
                        help="Update the document with the current date")
    parser.add_argument("--file-path", type=str, default=".",
                        help="Path to the directory containing the documents")
    args = parser.parse_args()


    documents = get_documents_due_for_review()
    # TODO: Output list of documents to stdout
    for document in documents:
        print(document)
    # TODO: If fix argument is passed, update the document with the current date
    if args.fix:
        print("Fixing documents")
        for document in documents:
            __fix_document(document)
        # TODO: Update the document with the current date

if __name__ == "__name__":
    main()
