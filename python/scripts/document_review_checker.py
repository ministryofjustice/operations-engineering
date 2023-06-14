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

def get_documents_due_for_review() -> list[str]:
    """Return a list of documents that are due for review"""
    # TODO: Get the root of the repository
    # TODO: Always look in the same place
    # TODO: Iterate over the files in the directory

    return ["document1", "document2"]


def __fix_document(document: str) -> None:
    # TODO: Update the document with the current date
    print(f"Fixing document {document}")
    pass

def main():
    # TODO: Check arguments
    parser = argparse.ArgumentParser(description="Document review checker")
    parser.add_argument("--fix", action="store_true",
                        help="Update the document with the current date")
    parser.add_argument("--file-path", type=str, default=".",
                        help="Path to the directory containing the documents")
    args = parser.parse_args()


    # TODO: Generate list of documents that are due for review
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
