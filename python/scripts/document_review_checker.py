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
from dateutil.relativedelta import relativedelta


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


    with open(document, 'r') as file:
        content = file.read()
        match = re.search(date_pattern, content)
        if match:
            date_str = match.group()
            date_format = "%Y-%m-%d"

            date_obj = datetime.strptime(date_str, date_format)
            if date_obj < today - relativedelta(months=3):
                return True

    return False

def fix_date(file_name: str) -> None:
    today = datetime.now().strftime('%Y-%m-%d')
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'

    with open(file_name, 'r') as file:
        content = file.read()

    updated_content = re.sub(date_pattern, today, content)

    with open(file_name, 'w') as file:
        file.write(updated_content)

    return None

def main():
    parser = argparse.ArgumentParser(description="Document review checker")
    parser.add_argument("--fix", action="store_true",
                        help="Update the document with the current date")
    parser.add_argument("--file-path", type=str, default=".",
                        help="Path to the directory containing the documents")
    args = parser.parse_args()


    docs_to_review = get_documents_due_for_review(args.file_path)
    for document in docs_to_review:
        print(document)
    if args.fix:
        print("Fixing documents")
        for document in docs_to_review:
            fix_date(document)

if __name__ == "__name__":
    main()
