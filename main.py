"""
This is an add-on to search a document for a regex and output all of the matches
"""

import csv
import re

from documentcloud.addon import AddOn
from documentcloud.exceptions import DoesNotExistError

class Regex(AddOn):
    """Uses re to find all regular expressions matches,
    outputs the results in a CSV, optionally annotates the document.
    """

    def main(self):
        """Main functionality"""
        if self.get_document_count() is None:
            self.set_message("Please select at least one document.")
            return
        regex = self.data["regex"]

        try:
            pattern = re.compile(regex)  # Attempt to compile the regex to confirm
        except re.error:
            self.set_message(f"Invalid regular expression provided: {regex}")
            return

        annotate = self.data["annotate"]
        access_level = self.data["annotation_access"]
        key = self.data.get("key").strip()

        with open("matches.csv", "w+", encoding="utf-8") as file_:
            writer = csv.writer(file_)
            writer.writerow(["match", "url", "page_number"])

            for document in self.get_documents():
                try:
                    document_text = document.full_text
                except DoesNotExistError:
                    self.set_message(f"Could not match regular expressions on document with id {document.id}, please OCR this document and run Regex Extractor again.")
                match = pattern.search(document_text)
                if match is not None:
                    match_string = match.group()
                    if key in document.data:
                        document.data[key].append(match_string)
                    else:
                        document.data[key] = [match_string]
                    document.save()
                # annotated_pages = set()
                for page_number in range(1, document.page_count + 1):
                    page_text = document.get_page_text(page_number)
                    matches = pattern.findall(page_text)
                    for match in matches:
                        writer.writerow([match, document.canonical_url, page_number])
                        if annotate:
                            # and page_number not in annotated_pages
                            document.annotations.create(
                                title=f"{match}",
                                page_number=page_number - 1,
                                access=access_level,
                            )
                            # annotated_pages.add(page_number)

            self.upload_file(file_)


if __name__ == "__main__":
    Regex().main()
